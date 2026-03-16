const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const { runHook } = require("../../helpers/run-hook");

describe("block-secrets.py", () => {
  // --- Passthrough: normal files ---

  it("allows normal source files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/src/index.js" },
    });
    assert.equal(exitCode, 0);
  });

  it("allows when no file_path is provided", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: {},
    });
    assert.equal(exitCode, 0);
  });

  it("allows config files that are not secrets", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/tsconfig.json" },
    });
    assert.equal(exitCode, 0);
  });

  // --- Blocked: env files ---

  it("blocks .env", async () => {
    const { exitCode, stderr } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/.env" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks .env.local", async () => {
    const { exitCode, stderr } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/.env.local" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks .env.production", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/.env.production" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .env.staging", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/.env.staging" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Blocked: credential files ---

  it("blocks credentials.json", async () => {
    const { exitCode, stderr } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/credentials.json" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /BLOCKED/i);
  });

  it("blocks secrets.json", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/secrets.json" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks serviceaccount.json", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/serviceaccount.json" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Blocked: SSH keys ---

  it("blocks id_rsa", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/home/user/.ssh/id_rsa" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks id_ed25519", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/home/user/.ssh/id_ed25519" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Blocked: package manager auth ---

  it("blocks .npmrc", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/.npmrc" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .pypirc", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/home/user/.pypirc" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Blocked: image/binary files ---

  it("blocks .png files", async () => {
    const { exitCode, stderr } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/logo.png" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /image/i);
  });

  it("blocks .jpg files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/photo.jpg" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .jpeg files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/photo.jpeg" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .gif files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/animation.gif" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .svg files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/icon.svg" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .webp files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/hero.webp" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .ico files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/favicon.ico" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .bmp files", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/image.bmp" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Blocked: secret directories ---

  it("blocks files in /.ssh/ directory", async () => {
    const { exitCode, stderr } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/home/user/.ssh/config" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /sensitive directory/i);
  });

  it("blocks files in /secrets/ directory", async () => {
    const { exitCode, stderr } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/secrets/api-key.txt" },
    });
    assert.equal(exitCode, 2);
    assert.match(stderr, /sensitive directory/i);
  });

  it("blocks files in /private/ directory", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/private/keys.txt" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Case insensitivity ---

  it("blocks .ENV (case insensitive)", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/.ENV" },
    });
    assert.equal(exitCode, 2);
  });

  it("blocks .PNG (case insensitive extension)", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "/project/logo.PNG" },
    });
    assert.equal(exitCode, 2);
  });

  // --- Windows backslash paths ---

  it("blocks secrets directory with Windows backslashes", async () => {
    const { exitCode } = await runHook("block-secrets.py", {
      tool_input: { file_path: "C:\\project\\secrets\\key.txt" },
    });
    assert.equal(exitCode, 2);
  });
});
