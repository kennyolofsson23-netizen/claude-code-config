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

  // --- Warns: dev server without tmux/screen (exit 0 with stderr warning) ---

  it("warns on npm run dev without multiplexer", async () => {
    const { exitCode, stderr } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "npm run dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
    assert.match(stderr, /WARNING.*orphaned|tmux|screen|run_in_background/i);
  });

  it("warns on npm start without multiplexer", async () => {
    const { exitCode, stderr } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "npm start" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
    assert.match(stderr, /WARNING/i);
  });

  it("warns on yarn dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "yarn dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on pnpm dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "pnpm dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on next dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "next dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on vite without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "vite" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on webpack serve without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "webpack serve" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on nodemon without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "nodemon server.js" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on uvicorn without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "uvicorn main:app --reload" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on flask run without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "flask run" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on python manage.py runserver without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "python manage.py runserver" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on cargo watch without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "cargo watch -x run" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on ts-node-dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "ts-node-dev src/index.ts" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });

  it("warns on bun dev without multiplexer", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "bun dev" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
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

  it("warns on case-insensitive matches (NPM RUN DEV)", async () => {
    const { exitCode } = await runHook(
      "block-dev-server.js",
      { tool_input: { command: "NPM RUN DEV" } },
      { env: { TMUX: "", STY: "" } }
    );
    assert.equal(exitCode, 0);
  });
});
