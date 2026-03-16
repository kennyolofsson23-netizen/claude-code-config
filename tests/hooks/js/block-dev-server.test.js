const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const { runHook } = require("../../helpers/run-hook");

describe("block-dev-server.js", () => {
  // --- Passthrough: non-dev-server commands ---

  it("allows non-dev-server commands", async () => {
    const { exitCode, stdout } = await runHook("block-dev-server.js", {
      tool_input: { command: "npm install express" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows when no command is provided", async () => {
    const { exitCode, stdout } = await runHook("block-dev-server.js", {});
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows npm test (not a dev server)", async () => {
    const { exitCode, stdout } = await runHook("block-dev-server.js", {
      tool_input: { command: "npm test" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  it("allows npm run build (not a dev server)", async () => {
    const { exitCode, stdout } = await runHook("block-dev-server.js", {
      tool_input: { command: "npm run build" },
    });
    assert.equal(exitCode, 0);
    assert.equal(JSON.parse(stdout).allowed, true);
  });

  // --- Blocked: dev server without tmux/screen ---

  it("blocks npm run dev without multiplexer", async () => {
    const { exitCode, stdout } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "npm run dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
    const out = JSON.parse(stdout);
    assert.equal(out.blocked, true);
    assert.match(out.reason, /tmux|screen/i);
  });

  it("blocks npm start without multiplexer", async () => {
    const { exitCode, stdout } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "npm start" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks yarn dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "yarn dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks pnpm dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "pnpm dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks next dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "next dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks vite without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "vite" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks webpack serve without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "webpack serve" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks nodemon without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "nodemon server.js" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks uvicorn without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "uvicorn main:app --reload" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks flask run without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "flask run" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks python manage.py runserver without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "python manage.py runserver" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks cargo watch without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "cargo watch -x run" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks ts-node-dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "ts-node-dev src/index.ts" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  it("blocks bun dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "bun dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });

  // --- Allowed: dev server inside tmux ---

  it("allows npm run dev inside tmux", async () => {
    const { exitCode, stdout } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "npm run dev" } },
      { env: { TMUX: "/tmp/tmux-1000/default,12345,0" } }
    );
    assert.equal(exitCode, 0);
    const out = JSON.parse(stdout);
    assert.equal(out.allowed, true);
    assert.equal(out.multiplexer, "tmux");
  });

  // --- Allowed: dev server inside screen ---

  it("allows npm run dev inside screen", async () => {
    const { exitCode, stdout } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "npm run dev" } },
      { env: { STY: "12345.pts-0.host" } }
    );
    assert.equal(exitCode, 0);
    const out = JSON.parse(stdout);
    assert.equal(out.allowed, true);
    assert.equal(out.multiplexer, "screen");
  });

  // --- Case insensitivity ---

  it("blocks case-insensitive matches (NPM RUN DEV)", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "NPM RUN DEV" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 1);
  });
});
