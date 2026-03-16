const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const { runHook } = require("../../helpers/run-hook");

describe("block-md-creation.js", () => {
  // --- Passthrough: non-.md files ---

  it("allows non-md files without warning", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/src/index.js" },
    });
    assert.equal(exitCode, 0);
    const out = JSON.parse(stdout);
    assert.equal(out.allowed, true);
  });

  it("allows when no file_path is provided", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {});
    assert.equal(exitCode, 0);
    const out = JSON.parse(stdout);
    assert.equal(out.allowed, true);
  });

  // --- Allowed .md patterns ---

  it("allows CLAUDE.md", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/CLAUDE.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows AGENTS.md", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/AGENTS.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows CHANGELOG.md", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/CHANGELOG.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows CODEMAP.md", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/CODEMAP.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows CONTRIBUTING.md", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/CONTRIBUTING.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows SKILL.md", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/.claude/skills/foo/SKILL.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows .md in /docs/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/docs/api-reference.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows .md in /documentation/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/documentation/setup.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows .md in /commands/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/.claude/commands/deploy.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows .md in /skills/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/.claude/skills/foo/bar.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows .md in /agents/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/.claude/agents/researcher.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows .md in /rules/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/.claude/rules/python.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows .md in /templates/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/templates/email.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  // --- Windows backslash paths ---

  it("allows .md in \\docs\\ directory (Windows paths)", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "C:\\project\\docs\\guide.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  // --- Warned: .md outside allowed directories ---

  it("warns for README.md (not in allowed list)", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/README.md" },
    });
    assert.equal(exitCode, 0);
    const out = JSON.parse(stdout);
    assert.ok(out.warning, "Expected a warning property");
    assert.match(out.warning, /README\.md/);
  });

  it("warns for arbitrary .md in project root", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/NOTES.md" },
    });
    assert.equal(exitCode, 0);
    const out = JSON.parse(stdout);
    assert.ok(out.warning, "Expected a warning property");
  });

  it("warns for .md in src/ directory", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { file_path: "/project/src/notes.md" },
    });
    assert.equal(exitCode, 0);
    const out = JSON.parse(stdout);
    assert.ok(out.warning);
  });

  // --- Edge: filePath alias ---

  it("accepts filePath alias for file_path", async () => {
    const { exitCode, stdout } = await runHook("block-md-creation.js", {
      tool_input: { filePath: "/project/docs/readme.md" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });
});
