const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const { runHook } = require("../../helpers/run-hook");

describe("block-dangerous.py", () => {
  // --- Passthrough: safe commands ---

  it("allows safe commands", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {
      tool_input: { command: "ls -la" },
    });
    assert.equal(exitCode, 0);
  });

  it("allows git push to feature branch", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {
      tool_input: { command: "git push origin feature/login" },
    });
    assert.equal(exitCode, 0);
  });

  it("exits 0 when no command is provided", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {
      tool_input: {},
    });
    assert.equal(exitCode, 0);
  });

  it("exits 0 with empty input", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {});
    assert.equal(exitCode, 0);
  });

  // --- Blocked: destructive file commands ---

  it("blocks rm -rf /", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "rm -rf /" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks rm -rf ~", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "rm -rf ~" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks rm -rf .", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "rm -rf ." },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  // --- Blocked: dangerous git commands ---

  it("blocks git push --force", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git push --force origin main" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks git push -f", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git push -f origin main" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks git reset --hard", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git reset --hard HEAD~3" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks git checkout -- .", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git checkout -- ." },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks git clean -fd", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git clean -fd" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks git clean -f", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git clean -f" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks git branch -D", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git branch -D feature/old" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  // --- Blocked: database destructive commands ---

  it("blocks drop database", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: 'psql -c "DROP DATABASE mydb"' },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks drop table", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: 'psql -c "DROP TABLE users"' },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks truncate table", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: 'psql -c "TRUNCATE TABLE users"' },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  // --- Blocked: production deploy commands ---

  it("blocks railway up", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "railway up" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks vercel --prod", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "vercel --prod" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks vercel deploy --prod", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "vercel deploy --prod" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  // --- Warned: push to main/master ---

  it("warns on git push origin main (exit 0)", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git push origin main" },
    });
    assert.equal(exitCode, 0);
    assert.match(stderr, /WARNING/i);
  });

  it("warns on git push origin master (exit 0)", async () => {
    const { exitCode, stderr } = await runHook("block-dangerous.py", {
      tool_input: { command: "git push origin master" },
    });
    assert.equal(exitCode, 0);
    assert.match(stderr, /WARNING/i);
  });

  // --- Safe branch delete is allowed ---

  it("allows git branch -d (safe delete, lowercase)", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {
      tool_input: { command: "git branch -d feature/old" },
    });
    assert.equal(exitCode, 0);
  });

  // --- Case insensitivity ---

  it("blocks case-insensitive matches (GIT RESET --HARD)", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {
      tool_input: { command: "GIT RESET --HARD" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Force push catch-all ---

  it("blocks git push with -f flag anywhere in command", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {
      tool_input: { command: "git push origin feature -f" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks git push with --force anywhere in command", async () => {
    const { exitCode } = await runHook("block-dangerous.py", {
      tool_input: { command: "git push origin feature --force" },
    });
    assert.equal(exitCode, 2);
  });
});
