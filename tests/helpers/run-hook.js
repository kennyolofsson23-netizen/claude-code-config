/**
 * Test helper: spawn a hook as a subprocess, pipe JSON on stdin, capture output.
 *
 * Usage:
 *   const { exitCode, stderr, stdout } = await runHook("commit-guard.js", {
 *     tool_input: { command: 'git commit -m "feat: add login"' }
 *   });
 */
const { spawn } = require("child_process");
const path = require("path");

const HOOKS_DIR = path.resolve(__dirname, "../../hooks");

/**
 * @param {string} hookFile - filename inside hooks/ (e.g. "commit-guard.js")
 * @param {object} stdinData - JSON object piped to the hook's stdin
 * @param {object} [opts] - extra options
 * @param {number} [opts.timeout=5000] - ms before killing the process
 * @returns {Promise<{exitCode: number, stdout: string, stderr: string}>}
 */
function runHook(hookFile, stdinData = {}, opts = {}) {
  const timeout = opts.timeout ?? 5000;
  const hookPath = path.join(HOOKS_DIR, hookFile);

  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [hookPath], {
      stdio: ["pipe", "pipe", "pipe"],
      env: { ...process.env, NODE_ENV: "test" },
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => { stdout += chunk; });
    child.stderr.on("data", (chunk) => { stderr += chunk; });

    const timer = setTimeout(() => {
      child.kill("SIGTERM");
      reject(new Error(`Hook ${hookFile} timed out after ${timeout}ms`));
    }, timeout);

    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ exitCode: code ?? 1, stdout: stdout.trim(), stderr: stderr.trim() });
    });

    child.on("error", (err) => {
      clearTimeout(timer);
      reject(err);
    });

    child.stdin.write(JSON.stringify(stdinData));
    child.stdin.end();
  });
}

module.exports = { runHook, HOOKS_DIR };
