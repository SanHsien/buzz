use axum::{
    body::Body,
    extract::{Request, State as AxumState},
    http::{HeaderMap, HeaderValue, StatusCode},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::get,
    Router,
};
use futures_util::TryStreamExt;
use tauri::{http, Manager};
use tokio::net::TcpListener;

use crate::app_state::AppState;
use crate::commands::media::mint_media_get_auth;
use crate::relay;

/// Defense-in-depth cap: refuse to buffer responses larger than this into RAM.
/// Range requests (≤16 MiB from server) always fit. Full GETs for huge videos
/// get a clear 413 instead of OOM — the <video> element always uses range
/// requests for seeking, so this only catches edge cases.
const MAX_PROXY_RESPONSE: u64 = 20 * 1024 * 1024;

#[derive(Clone)]
struct ProxyState {
    client: reqwest::Client,
    app_handle: tauri::AppHandle,
}

// fork patch (SanHsien/buzz): Host/Origin guard against DNS rebinding for the loopback
// media proxy (docs/fork/DECISIONS.md, 2026-11-23); on a sync conflict upstream wins,
// then redo the guard if upstream has not added its own.

/// Origins the app's own webview sends: Tauri serves the packaged app from
/// `tauri://localhost` (macOS/Linux) or `http://tauri.localhost` (Windows).
const TRUSTED_ORIGINS: &[&str] = &["tauri://localhost", "http://tauri.localhost"];

/// The Vite dev server (`devUrl` in `tauri.conf.json`); trusted in debug builds only,
/// as in `linux_media.rs`.
#[cfg(debug_assertions)]
const DEV_ORIGIN: &str = "http://localhost:1420";

/// Whether a `Host` header names this loopback proxy. A DNS-rebound page reaches the
/// listener with its attacker-controlled name (`evil.example:PORT`) in `Host`, so only a
/// loopback name is accepted, with no port or with this proxy's own port.
fn is_own_loopback_host(host: &str, own_port: u16) -> bool {
    let host = host.trim().to_ascii_lowercase();
    let (name, tail) = if host.starts_with('[') {
        let Some(end) = host.find(']') else {
            return false;
        };
        host.split_at(end + 1)
    } else {
        match host.find(':') {
            Some(at) => host.split_at(at),
            None => (host.as_str(), ""),
        }
    };
    if !matches!(name, "127.0.0.1" | "localhost" | "[::1]") {
        return false;
    }
    match tail.strip_prefix(':') {
        None => tail.is_empty(),
        Some(port) => {
            !port.is_empty()
                && port.bytes().all(|b| b.is_ascii_digit())
                && port.parse::<u16>().is_ok_and(|p| p == own_port)
        }
    }
}

/// Whether an `Origin` header is one of the desktop app's own origins.
fn is_trusted_origin(origin: &str) -> bool {
    if TRUSTED_ORIGINS.contains(&origin) {
        return true;
    }
    #[cfg(debug_assertions)]
    if origin == DEV_ORIGIN {
        return true;
    }
    false
}

/// Reject requests that did not come from this machine's loopback or the app's webview.
/// A request without `Origin` (a plain `<video>`/`<img>` load) passes; one with `Origin`
/// must carry an app origin. The `Host` check is what stops DNS rebinding, because a
/// rebound page is same-origin with the attacker's name and may send no `Origin` at all.
async fn reject_foreign_requests(
    AxumState(own_port): AxumState<u16>,
    req: Request,
    next: Next,
) -> Response {
    let headers = req.headers();
    let host_ok = headers
        .get("host")
        .and_then(|v| v.to_str().ok())
        .is_some_and(|h| is_own_loopback_host(h, own_port));
    if !host_ok {
        return (StatusCode::FORBIDDEN, "forbidden: invalid host").into_response();
    }
    if let Some(origin) = headers.get("origin") {
        if !origin.to_str().is_ok_and(is_trusted_origin) {
            return (StatusCode::FORBIDDEN, "forbidden: invalid origin").into_response();
        }
    }
    next.run(req).await
}

/// Put the Host/Origin guard in front of every route of `router`.
fn with_loopback_guard(router: Router, own_port: u16) -> Router {
    router.layer(middleware::from_fn_with_state(
        own_port,
        reject_foreign_requests,
    ))
}

async fn proxy_handler(AxumState(state): AxumState<ProxyState>, req: Request) -> Response {
    let path_and_query = req
        .uri()
        .path_and_query()
        .map(|pq| pq.as_str())
        .unwrap_or("/");

    // Resolve relay URL dynamically so workspace switches take effect immediately.
    let app_state = state.app_handle.state::<AppState>();
    let base_url = relay::relay_api_base_url_with_override(&app_state);
    let upstream_url = format!("{base_url}{path_and_query}");

    let has_range = req.headers().contains_key("range");

    let mut upstream = state
        .client
        .get(&upstream_url)
        .timeout(std::time::Duration::from_secs(120));

    // `upstream_url` is always `{relay base}{path}`, so the token can't reach
    // a third-party origin (mint_media_get_auth safety contract).
    if let Some(auth) = mint_media_get_auth(&app_state, &base_url) {
        upstream = upstream.header("authorization", auth);
    }

    if let Some(range) = req.headers().get("range") {
        if let Ok(v) = range.to_str() {
            upstream = upstream.header("range", v);
        }
    }

    let resp = match upstream.send().await {
        Ok(r) => r,
        Err(_) => {
            return (StatusCode::BAD_GATEWAY, "upstream request failed").into_response();
        }
    };

    // Re-mint and retry once on an auth failure (401 missing_evidence or 403
    // evidence_rejected). Under NIP-FI strict mode a read token expires after
    // 60s, so a long video range-request stream will exhaust its token mid-flight.
    // Single retry; if the fresh token also fails, propagate the error to the caller.
    let resp = if (resp.status() == reqwest::StatusCode::UNAUTHORIZED
        || resp.status() == reqwest::StatusCode::FORBIDDEN)
        && has_range
    {
        if let Some(fresh_auth) = mint_media_get_auth(&app_state, &base_url) {
            let mut retry = state
                .client
                .get(&upstream_url)
                .timeout(std::time::Duration::from_secs(120))
                .header("authorization", fresh_auth);
            if let Some(range) = req.headers().get("range") {
                if let Ok(v) = range.to_str() {
                    retry = retry.header("range", v);
                }
            }
            match retry.send().await {
                Ok(r) => r,
                Err(_) => {
                    return (StatusCode::BAD_GATEWAY, "upstream request failed").into_response();
                }
            }
        } else {
            resp
        }
    } else {
        resp
    };

    let status =
        StatusCode::from_u16(resp.status().as_u16()).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR);

    let mut headers = HeaderMap::new();
    for key in &[
        "content-type",
        "content-range",
        "accept-ranges",
        "content-length",
        // Cache-related headers — let WKWebView's HTTP cache do its job so
        // images don't re-fetch on every channel switch. Media URLs are
        // content-addressed (sha256 in path), so the relay sends
        // `Cache-Control: public, max-age=31536000, immutable` and we
        // forward it verbatim. `etag`/`last-modified` are forwarded for
        // future-proofing if upstream ever adds them.
        "cache-control",
        "etag",
        "last-modified",
    ] {
        if let Some(val) = resp.headers().get(*key) {
            if let Ok(v) = HeaderValue::from_bytes(val.as_bytes()) {
                headers.insert(*key, v);
            }
        }
    }

    // OOM guard for non-range full GETs (same 20 MB cap as the protocol handler).
    if !has_range {
        if let Some(cl) = headers.get("content-length") {
            if let Ok(len) = cl.to_str().unwrap_or("0").parse::<u64>() {
                if len > MAX_PROXY_RESPONSE {
                    return (
                        StatusCode::PAYLOAD_TOO_LARGE,
                        "response too large — use range requests for video playback",
                    )
                        .into_response();
                }
            }
        }
    }

    // Stream the body — no buffering.
    let stream = resp.bytes_stream().map_err(std::io::Error::other);
    let body = Body::from_stream(stream);

    (status, headers, body).into_response()
}

/// Spawn a localhost HTTP proxy that streams media via reqwest, avoiding the
/// Tauri protocol handler's requirement to buffer the entire response into
/// `Vec<u8>`. Returns the OS-assigned port.
pub async fn spawn_media_proxy(http_client: reqwest::Client, app_handle: tauri::AppHandle) -> u16 {
    let proxy_state = ProxyState {
        client: http_client,
        app_handle,
    };

    let listener = TcpListener::bind("127.0.0.1:0")
        .await
        .expect("failed to bind media proxy");
    let port = listener.local_addr().unwrap().port();

    let app = with_loopback_guard(
        Router::new()
            .route("/media/{*path}", get(proxy_handler))
            .with_state(proxy_state),
        port,
    );

    tokio::spawn(async move {
        axum::serve(listener, app).await.ok();
    });

    eprintln!("buzz-desktop: media proxy listening on 127.0.0.1:{port}");
    port
}

/// Proxy media requests through the Rust backend so they traverse the VPN tunnel.
///
/// WKWebView's networking stack bypasses the VPN tunnel, causing 403s from Cloudflare Access.
/// This handler routes `buzz-media://localhost/{path}` through reqwest, which
/// runs in the Tauri process and goes through the VPN.
pub async fn handle_buzz_media(
    app: &tauri::AppHandle,
    request: &http::Request<Vec<u8>>,
) -> http::Response<Vec<u8>> {
    use tauri::Manager;

    let state = app.state::<AppState>();
    let base = relay::relay_api_base_url_with_override(&state);

    // Preserve path + query (thumbnails may have query params).
    // Only proxy /media/ paths — reject anything else.
    let path_and_query = request
        .uri()
        .path_and_query()
        .map(|pq| pq.as_str())
        .unwrap_or("/");

    if !path_and_query.starts_with("/media/") {
        return error_response(404, "not found");
    }

    let has_range = request.headers().contains_key("range");
    let upstream_url = format!("{base}{path_and_query}");

    // Forward Range header if present — enables video seeking through the proxy.
    let mut upstream = state
        .http_client
        .get(&upstream_url)
        .timeout(std::time::Duration::from_secs(60));

    // `upstream_url` is always `{relay base}{path}`, so the token can't reach
    // a third-party origin (mint_media_get_auth safety contract).
    if let Some(auth) = mint_media_get_auth(&state, &base) {
        upstream = upstream.header("authorization", auth);
    }

    if let Some(range) = request.headers().get("range") {
        if let Ok(v) = range.to_str() {
            upstream = upstream.header("range", v);
        }
    }

    let result = upstream.send().await;

    // Re-mint and retry once on auth failure (401/403) for range requests.
    // Under NIP-FI strict mode a read token expires after 60s, exhausting
    // mid-stream. Single retry with a fresh token; propagate on second failure.
    let result = match result {
        Ok(resp)
            if (resp.status() == reqwest::StatusCode::UNAUTHORIZED
                || resp.status() == reqwest::StatusCode::FORBIDDEN)
                && has_range =>
        {
            if let Some(fresh_auth) = mint_media_get_auth(&state, &base) {
                let mut retry = state
                    .http_client
                    .get(&upstream_url)
                    .timeout(std::time::Duration::from_secs(60))
                    .header("authorization", fresh_auth);
                if let Some(range) = request.headers().get("range") {
                    if let Ok(v) = range.to_str() {
                        retry = retry.header("range", v);
                    }
                }
                retry.send().await
            } else {
                Ok(resp)
            }
        }
        other => other,
    };

    match result {
        Ok(resp) => {
            let status = resp.status().as_u16();
            let content_type = resp
                .headers()
                .get("content-type")
                .and_then(|v| v.to_str().ok())
                .unwrap_or("application/octet-stream")
                .to_string();

            // Propagate range-related headers so <video> seeking works.
            let content_range = resp
                .headers()
                .get("content-range")
                .and_then(|v| v.to_str().ok())
                .map(|s| s.to_string());
            let accept_ranges = resp
                .headers()
                .get("accept-ranges")
                .and_then(|v| v.to_str().ok())
                .map(|s| s.to_string());
            let content_length = resp
                .headers()
                .get("content-length")
                .and_then(|v| v.to_str().ok())
                .map(|s| s.to_string());

            // Propagate cache-related headers so WKWebView's HTTP cache
            // can avoid re-fetching content-addressed media on every
            // channel switch. The relay sends
            // `Cache-Control: public, max-age=31536000, immutable`;
            // `etag`/`last-modified` are forwarded if upstream supplies them.
            let cache_control = resp
                .headers()
                .get("cache-control")
                .and_then(|v| v.to_str().ok())
                .map(|s| s.to_string());
            let etag = resp
                .headers()
                .get("etag")
                .and_then(|v| v.to_str().ok())
                .map(|s| s.to_string());
            let last_modified = resp
                .headers()
                .get("last-modified")
                .and_then(|v| v.to_str().ok())
                .map(|s| s.to_string());

            // OOM guard: if this is a non-range GET and the upstream body is
            // larger than our cap, bail with 413 instead of buffering into RAM.
            // Tauri's protocol handler requires Vec<u8> so we can't truly stream.
            if !has_range {
                if let Some(ref cl) = content_length {
                    if let Ok(len) = cl.parse::<u64>() {
                        if len > MAX_PROXY_RESPONSE {
                            return error_response(
                                413,
                                "response too large — use range requests for video playback",
                            );
                        }
                    }
                }
            }

            match resp.bytes().await {
                Ok(bytes) => {
                    let mut builder = http::Response::builder()
                        .status(status)
                        .header("content-type", &content_type);
                    if let Some(ref cr) = content_range {
                        builder = builder.header("content-range", cr);
                    }
                    if let Some(ref ar) = accept_ranges {
                        builder = builder.header("accept-ranges", ar);
                    }
                    if let Some(ref cl) = content_length {
                        builder = builder.header("content-length", cl);
                    }
                    if let Some(ref cc) = cache_control {
                        builder = builder.header("cache-control", cc);
                    }
                    if let Some(ref e) = etag {
                        builder = builder.header("etag", e);
                    }
                    if let Some(ref lm) = last_modified {
                        builder = builder.header("last-modified", lm);
                    }
                    builder
                        .body(bytes.to_vec())
                        .unwrap_or_else(|_| error_response(500, "response build failed"))
                }
                Err(_) => error_response(502, "failed to read upstream body"),
            }
        }
        Err(_) => error_response(502, "upstream request failed"),
    }
}

fn error_response(status: u16, msg: &str) -> http::Response<Vec<u8>> {
    http::Response::builder()
        .status(status)
        .header("content-type", "text/plain")
        .body(msg.as_bytes().to_vec())
        .unwrap_or_else(|_| {
            http::Response::builder()
                .status(500)
                .body(Vec::new())
                .unwrap()
        })
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Serve `with_loopback_guard` over a trivial route on a real loopback socket, so the
    /// tests send actual `Host`/`Origin` headers instead of calling the helpers directly.
    async fn spawn_guarded_test_server() -> u16 {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let port = listener.local_addr().unwrap().port();
        let app = with_loopback_guard(
            Router::new().route("/media/{*path}", get(|| async { "media bytes" })),
            port,
        );
        tokio::spawn(async move {
            axum::serve(listener, app).await.ok();
        });
        port
    }

    async fn get_status(port: u16, host: Option<&str>, origin: Option<&str>) -> u16 {
        let mut req = reqwest::Client::new().get(format!("http://127.0.0.1:{port}/media/abc.png"));
        if let Some(host) = host {
            req = req.header("host", host);
        }
        if let Some(origin) = origin {
            req = req.header("origin", origin);
        }
        req.send().await.unwrap().status().as_u16()
    }

    #[tokio::test]
    async fn dns_rebound_host_is_refused_with_403() {
        let port = spawn_guarded_test_server().await;
        // The rebound page's own name arrives in `Host`, with or without an Origin.
        assert_eq!(
            get_status(port, Some(&format!("evil.example.com:{port}")), None).await,
            403
        );
        assert_eq!(get_status(port, Some("evil.example.com"), None).await, 403);
        // Look-alikes of a loopback name are not loopback.
        assert_eq!(
            get_status(port, Some(&format!("localhost.evil.com:{port}")), None).await,
            403
        );
        assert_eq!(
            get_status(port, Some(&format!("127.0.0.1.evil.com:{port}")), None).await,
            403
        );
        // A loopback name with another service's port is not this proxy.
        let other_port = u32::from(port) + 1;
        assert_eq!(
            get_status(port, Some(&format!("localhost:{other_port}")), None).await,
            403
        );
    }

    #[tokio::test]
    async fn foreign_origin_is_refused_with_403_even_with_a_loopback_host() {
        let port = spawn_guarded_test_server().await;
        for origin in [
            "https://evil.example.com",
            "http://localhost:3000",
            "tauri://localhost.evil.com",
            "null",
        ] {
            assert_eq!(
                get_status(port, None, Some(origin)).await,
                403,
                "origin {origin} must be refused"
            );
        }
    }

    #[tokio::test]
    async fn loopback_request_without_origin_or_from_the_app_passes() {
        let port = spawn_guarded_test_server().await;
        // `<video>`/`<img>` loads send no Origin; reqwest's default Host is 127.0.0.1:PORT.
        assert_eq!(get_status(port, None, None).await, 200);
        assert_eq!(
            get_status(port, Some(&format!("localhost:{port}")), None).await,
            200
        );
        assert_eq!(
            get_status(port, Some(&format!("[::1]:{port}")), None).await,
            200
        );
        for origin in ["tauri://localhost", "http://tauri.localhost"] {
            assert_eq!(get_status(port, None, Some(origin)).await, 200, "{origin}");
        }
    }

    #[test]
    fn host_parsing_accepts_only_loopback_names_with_the_own_port() {
        assert!(is_own_loopback_host("127.0.0.1:4000", 4000));
        assert!(is_own_loopback_host("LOCALHOST:4000", 4000));
        assert!(is_own_loopback_host("[::1]:4000", 4000));
        assert!(is_own_loopback_host("localhost", 4000));
        assert!(!is_own_loopback_host("", 4000));
        assert!(!is_own_loopback_host("localhost:", 4000));
        assert!(!is_own_loopback_host("localhost:+4000", 4000));
        assert!(!is_own_loopback_host("localhost:4000x", 4000));
        assert!(!is_own_loopback_host("localhost:4001", 4000));
        assert!(!is_own_loopback_host("[::1", 4000));
        assert!(!is_own_loopback_host("[::2]:4000", 4000));
        assert!(!is_own_loopback_host("127.0.0.2:4000", 4000));
        assert!(!is_own_loopback_host("10.0.0.5:4000", 4000));
    }

    #[cfg(debug_assertions)]
    #[test]
    fn dev_server_origin_is_trusted_in_debug_builds_only() {
        assert!(is_trusted_origin("http://localhost:1420"));
        assert!(!is_trusted_origin("http://localhost:14200"));
    }
}
