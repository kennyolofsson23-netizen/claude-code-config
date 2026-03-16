const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const { runHook } = require("../../helpers/run-hook");

const HOOK = "validate-agent-schema.js";

/**
 * Helper: build a Write tool_input for an agent file.
 */
function agentWrite(filename, content) {
  return {
    tool_input: {
      file_path: `/home/user/.claude/agents/${filename}`,
      content,
    },
  };
}

/**
 * Helper: build valid agent frontmatter + body.
 */
function validAgent(overrides = {}) {
  const fm = {
    name: "test-agent",
    description: "A test agent for validation",
    model: "sonnet",
    tools: ["Read", "Write", "Bash"],
    ...overrides,
  };
  // Build YAML frontmatter manually
  let yaml = `---\nname: ${fm.name}\n`;
  if (fm.description !== undefined) yaml += `description: ${fm.description}\n`;
  yaml += `model: ${fm.model}\n`;
  if (fm.memory) yaml += `memory: ${fm.memory}\n`;
  if (Array.isArray(fm.tools)) {
    yaml += "tools:\n";
    for (const t of fm.tools) yaml += `  - ${t}\n`;
  } else if (fm.tools !== undefined) {
    // raw tools line for testing invalid formats
    yaml += `tools: ${fm.tools}\n`;
  }
  yaml += "---\n\n# Test Agent\n\nYou are a test agent.";
  return yaml;
}

describe("validate-agent-schema.js", () => {
  // === PASSTHROUGH (non-agent files) ===

  it("allows non-agent file paths", async () => {
    const { exitCode } = await runHook(HOOK, {
      tool_input: {
        file_path: "/project/src/index.js",
        content: "console.log('hello');",
      },
    });
    assert.equal(exitCode, 0);
  });

  it("allows when no file_path is provided", async () => {
    const { exitCode } = await runHook(HOOK, { tool_input: {} });
    assert.equal(exitCode, 0);
  });

  it("allows empty input", async () => {
    const { exitCode } = await runHook(HOOK, {});
    assert.equal(exitCode, 0);
  });

  it("allows .md files outside agents/ directory", async () => {
    const { exitCode } = await runHook(HOOK, {
      tool_input: {
        file_path: "/project/docs/README.md",
        content: "# README",
      },
    });
    assert.equal(exitCode, 0);
  });

  // === VALID AGENTS ===

  it("accepts a fully valid agent file", async () => {
    const content = validAgent();
    const { exitCode } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
  });

  it("accepts valid agent with memory: project", async () => {
    const content = validAgent({ memory: "project" });
    const { exitCode } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
  });

  it("accepts valid agent with memory: user", async () => {
    const content = validAgent({ memory: "user" });
    const { exitCode } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
  });

  it("accepts valid agent with model: opus", async () => {
    const content = validAgent({ model: "opus" });
    const { exitCode } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
  });

  it("accepts valid agent with model: haiku", async () => {
    const content = validAgent({ model: "haiku" });
    const { exitCode } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
  });

  it("accepts agent with MCP tools", async () => {
    const content = validAgent({
      tools: ["Read", "Bash", "mcp__context7__query-docs"],
    });
    const { exitCode } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
  });

  it("accepts agent with wildcard MCP tools", async () => {
    const content = validAgent({
      tools: ["Read", "mcp__ux-best-practices__*"],
    });
    const { exitCode } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
  });

  it("accepts Windows-style paths to agents/ directory", async () => {
    const content = validAgent();
    const { exitCode } = await runHook(HOOK, {
      tool_input: {
        file_path: "C:\\Users\\Kenny\\.claude\\agents\\test-agent.md",
        content,
      },
    });
    assert.equal(exitCode, 0);
  });

  // === BLOCKING: Missing required fields ===

  it("blocks agent missing name field", async () => {
    const content = "---\nmodel: sonnet\ndescription: test\ntools:\n  - Read\n---\n\n# Agent";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /name/i);
  });

  it("blocks agent missing model field", async () => {
    const content = "---\nname: test\ndescription: test\ntools:\n  - Read\n---\n\n# Agent";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /model/i);
  });

  it("blocks agent missing tools field", async () => {
    const content = "---\nname: test\ndescription: test\nmodel: sonnet\n---\n\n# Agent";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /tools/i);
  });

  it("blocks agent with no frontmatter at all", async () => {
    const content = "# Agent\n\nNo frontmatter here.";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /frontmatter/i);
  });

  it("blocks agent with empty frontmatter", async () => {
    const content = "---\n---\n\n# Agent";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
  });

  // === BLOCKING: Invalid values ===

  it("blocks invalid model value", async () => {
    const content = validAgent({ model: "gpt-4" });
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /model/i);
  });

  it("blocks invalid memory value", async () => {
    const content = validAgent({ memory: "global" });
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /memory/i);
  });

  it("blocks JSON-array tools format", async () => {
    const content =
      '---\nname: test\ndescription: test\nmodel: sonnet\ntools: ["Read", "Bash"]\n---\n\n# Agent';
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /tools/i);
  });

  it("blocks empty tools array", async () => {
    const content = "---\nname: test\ndescription: test\nmodel: sonnet\ntools:\n---\n\n# Agent";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /tools/i);
  });

  // === WARNINGS (exit 0 with message) ===

  it("warns when description is missing", async () => {
    const content = "---\nname: test\nmodel: sonnet\ntools:\n  - Read\n---\n\n# Agent";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 0);
    assert.match(stderr, /description/i);
  });

  it("warns when name doesn't match filename", async () => {
    const content = validAgent({ name: "wrong-name" });
    const { exitCode, stderr } = await runHook(
      HOOK,
      agentWrite("actual-name.md", content)
    );
    assert.equal(exitCode, 0);
    assert.match(stderr, /name.*match|mismatch/i);
  });

  // === EDGE CASES ===

  it("handles non-.md files in agents/ directory", async () => {
    const { exitCode } = await runHook(HOOK, {
      tool_input: {
        file_path: "/home/user/.claude/agents/config.json",
        content: "{}",
      },
    });
    assert.equal(exitCode, 0);
  });

  it("handles content with no closing frontmatter delimiter", async () => {
    const content = "---\nname: test\nmodel: sonnet\n# No closing ---";
    const { exitCode, stderr } = await runHook(HOOK, agentWrite("test-agent.md", content));
    assert.equal(exitCode, 2);
    assert.match(stderr, /frontmatter/i);
  });

  it("accepts permissionMode field", async () => {
    const content =
      "---\nname: qa\ndescription: QA agent\nmodel: sonnet\npermissionMode: acceptEdits\ntools:\n  - Read\n  - Write\n---\n\n# QA";
    const { exitCode } = await runHook(HOOK, agentWrite("qa.md", content));
    assert.equal(exitCode, 0);
  });
});
