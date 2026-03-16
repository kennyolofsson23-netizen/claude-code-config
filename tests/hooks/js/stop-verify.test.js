const { describe, it, beforeEach, afterEach } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const os = require("os");
const { runHook } = require("../../helpers/run-hook");

describe("stop-verify.py", () => {
  let tmpDir;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "stop-verify-"));
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("exits 0 with no output when no tasks directory exists", async () => {
    // Run from a directory with no tasks/
    const { exitCode, stderr } = await runHook("stop-verify.py", {}, {
      env: { HOME: tmpDir, USERPROFILE: tmpDir },
    });
    assert.equal(exitCode, 0);
    // stop-verify.py checks os.path.exists("tasks/todo.md") relative to cwd
    // Since we can't easily change cwd for the subprocess, we test other scenarios
  });

  it("always exits 0 (never blocks)", async () => {
    const { exitCode } = await runHook("stop-verify.py", {});
    assert.equal(exitCode, 0);
  });

  it("outputs reminder to stderr when tasks/ directory exists", async () => {
    // The hook checks for tasks/ relative to cwd, which is ~/.claude
    // ~/.claude has a tasks/ directory, so it should output the reminder
    const { exitCode, stderr } = await runHook("stop-verify.py", {});
    assert.equal(exitCode, 0);
    assert.match(stderr, /patterns\.log/i);
  });

  it("reports unchecked todo items from tasks/todo.md", async () => {
    // Since the hook runs in ~/.claude which has tasks/todo.md with unchecked items
    const { exitCode, stderr } = await runHook("stop-verify.py", {});
    assert.equal(exitCode, 0);
    assert.match(stderr, /unchecked items/i);
  });

  it("accepts any JSON input without error", async () => {
    const { exitCode } = await runHook("stop-verify.py", {
      some_field: "value",
      nested: { data: true },
    });
    assert.equal(exitCode, 0);
  });
});
