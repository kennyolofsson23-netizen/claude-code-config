const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const { runHook } = require("../../helpers/run-hook");

/** Helper: build hook input for a git commit command */
function commitInput(msg) {
  return { tool_input: { command: `git commit -m "${msg}"` } };
}

describe("commit-guard.js", () => {
  // --- Passthrough cases ---

  it("exits 0 for non-git-commit commands", async () => {
    const { exitCode } = await runHook("commit-guard.js", {
      tool_input: { command: "ls -la" },
    });
    assert.equal(exitCode, 0);
  });

  it("exits 0 when no command is provided", async () => {
    const { exitCode } = await runHook("commit-guard.js", {});
    assert.equal(exitCode, 0);
  });

  it("exits 0 when stdin is empty JSON", async () => {
    const { exitCode } = await runHook("commit-guard.js", {});
    assert.equal(exitCode, 0);
  });

  // --- Valid messages ---

  it("accepts valid conventional commit: feat: add login", async () => {
    const { exitCode } = await runHook("commit-guard.js", commitInput("feat: add login"));
    assert.equal(exitCode, 0);
  });

  it("accepts valid commit with scope: feat(auth): add login", async () => {
    const { exitCode } = await runHook("commit-guard.js", commitInput("feat(auth): add login"));
    assert.equal(exitCode, 0);
  });

  it("accepts all conventional types", async () => {
    const types = ["feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "ci", "build", "revert"];
    for (const type of types) {
      const { exitCode } = await runHook("commit-guard.js", commitInput(`${type}: do something`));
      assert.equal(exitCode, 0, `Expected exit 0 for type "${type}"`);
    }
  });

  // --- Invalid messages ---

  it("rejects non-conventional format: added login", async () => {
    const { exitCode, stderr } = await runHook("commit-guard.js", commitInput("added login"));
    assert.equal(exitCode, 2);
    assert.match(stderr, /conventional commit/i);
  });

  it("rejects subject line over 72 chars", async () => {
    const longMsg = "feat: " + "a".repeat(67); // 73 chars total
    const { exitCode, stderr } = await runHook("commit-guard.js", commitInput(longMsg));
    assert.equal(exitCode, 2);
    assert.match(stderr, /chars/i);
  });

  it("rejects subject line ending with period", async () => {
    const { exitCode, stderr } = await runHook("commit-guard.js", commitInput("feat: add login."));
    assert.equal(exitCode, 2);
    assert.match(stderr, /period/i);
  });

  it("rejects uppercase description", async () => {
    const { exitCode, stderr } = await runHook("commit-guard.js", commitInput("feat: Add login"));
    assert.equal(exitCode, 2);
    assert.match(stderr, /lowercase/i);
  });

  it("reports multiple errors at once", async () => {
    const longMsg = "Added login page with lots of features and stuff that nobody asked for really.";
    const { exitCode, stderr } = await runHook("commit-guard.js", commitInput(longMsg));
    assert.equal(exitCode, 2);
    // Should have at least conventional format + uppercase errors
    const errorLines = stderr.split("\n").filter((l) => l.trim().startsWith("-"));
    assert.ok(errorLines.length >= 2, `Expected 2+ errors, got ${errorLines.length}`);
  });

  // --- Edge cases ---

  it("handles breaking change marker: feat!: change api", async () => {
    const { exitCode } = await runHook("commit-guard.js", commitInput("feat!: change api"));
    // The regex has !? before the colon, so this should pass
    assert.equal(exitCode, 0);
  });

  it("exits 0 for git commit without -m flag", async () => {
    const { exitCode } = await runHook("commit-guard.js", {
      tool_input: { command: "git commit" },
    });
    assert.equal(exitCode, 0);
  });
});
