import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

// Every @tiptap/* package pins its siblings with an exact peer range
// (e.g. extension-bubble-menu 3.33.0 wants @tiptap/core 3.33.0). @tiptap/react
// lists bubble-menu and floating-menu as optionalDependencies with a caret
// range, so a lock refresh floats them to the newest release while core stays
// put. The mixed set installs without error but violates those exact peer
// ranges. (It was found alongside, but is not the cause of, the 2026-11-08
// destroyed-editor `commands` throw; see docs/fork/DECISIONS.md.)
const lockUrl = new URL("../../pnpm-lock.yaml", import.meta.url);

test("pnpm-lock resolves every @tiptap/* package to one version", () => {
  const lock = readFileSync(lockUrl, "utf8");
  const packages = lock.slice(lock.indexOf("\npackages:\n"));
  const end = packages.indexOf("\nsnapshots:\n");
  const section = end === -1 ? packages : packages.slice(0, end);

  // name@version entries, so two versions of one package are both counted
  const entries = [];
  for (const match of section.matchAll(
    /^ {2}'(@tiptap\/[^@']+)@([^']+)':$/gm,
  )) {
    const [, name, version] = match;
    entries.push(`${name}@${version}`);
  }

  assert.ok(entries.length > 10, "expected the @tiptap/* packages in the lock");
  const distinct = new Set(entries.map((e) => e.slice(e.lastIndexOf("@") + 1)));
  assert.equal(
    distinct.size,
    1,
    `@tiptap/* versions must match, got ${JSON.stringify(entries)}`,
  );
});
