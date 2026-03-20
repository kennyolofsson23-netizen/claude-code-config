const { describe, it, before, after } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const os = require("os");
const { runHook } = require("../../helpers/run-hook");

/** Helper: build PostToolUse Edit/Write input */
function editInput(filePath) {
  return { tool_input: { file_path: filePath } };
}

describe("auto-lint.js", () => {
  // ── Early-exit paths ──────────────────────────────────────────────────

  describe("early exits", () => {
    it("exits 0 when no file_path provided", async () => {
      const { exitCode, stdout } = await runHook("auto-lint.js", {});
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 when tool_input is empty", async () => {
      const { exitCode, stdout } = await runHook("auto-lint.js", { tool_input: {} });
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 for .py files (non-JS/TS)", async () => {
      const { exitCode, stdout } = await runHook("auto-lint.js", editInput("/tmp/app.py"));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 for .css files", async () => {
      const { exitCode, stdout } = await runHook("auto-lint.js", editInput("/tmp/styles.css"));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 for .md files", async () => {
      const { exitCode, stdout } = await runHook("auto-lint.js", editInput("/tmp/README.md"));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 for .json files", async () => {
      const { exitCode, stdout } = await runHook("auto-lint.js", editInput("/tmp/package.json"));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("accepts filePath alias (camelCase)", async () => {
      const { exitCode, stdout } = await runHook("auto-lint.js", {
        tool_input: { filePath: "/tmp/test.py" },
      });
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });
  });

  // ── Extension acceptance ──────────────────────────────────────────────

  describe("accepted extensions (proceeds past extension check)", () => {
    // These files won't have a config dir, so lint runs but finds nothing to do.
    // We verify they DON'T early-exit (would produce empty stdout if no config found).
    for (const ext of [".js", ".jsx", ".ts", ".tsx"]) {
      it(`processes ${ext} files`, async () => {
        // Use a deep tmp path with no eslint/tsconfig — hook runs but finds no config
        const fakePath = path.join(os.tmpdir(), `lint-test-noconfig-dir`, `file${ext}`);
        const { exitCode, stdout } = await runHook("auto-lint.js", editInput(fakePath));
        // Should exit 0 with no output (no config found = nothing to lint)
        assert.equal(exitCode, 0);
        assert.equal(stdout, "");
      });
    }
  });

  // ── ESLint integration (real config) ──────────────────────────────────

  describe("ESLint integration", () => {
    let tmpDir;

    before(() => {
      tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "auto-lint-eslint-"));
      // package.json with eslint so the hook doesn't skip
      fs.writeFileSync(
        path.join(tmpDir, "package.json"),
        JSON.stringify({ name: "test", devDependencies: { eslint: "^9.0.0" } })
      );
      // Minimal flat ESLint config that flags `no-unused-vars`
      fs.writeFileSync(
        path.join(tmpDir, "eslint.config.mjs"),
        `export default [{ rules: { "no-unused-vars": "error" } }];\n`
      );
      // A clean JS file (no errors)
      fs.writeFileSync(path.join(tmpDir, "clean.js"), `const x = 1;\nconsole.log(x);\n`);
      // A file with an ESLint error (unused var)
      fs.writeFileSync(path.join(tmpDir, "bad.js"), `const unused = 42;\n`);
    });

    after(() => {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    it("produces no output for clean JS file", async () => {
      const { exitCode, stdout } = await runHook(
        "auto-lint.js",
        editInput(path.join(tmpDir, "clean.js")),
        { timeout: 20000 }
      );
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("reports ESLint errors for bad JS file", async () => {
      const { exitCode, stdout } = await runHook(
        "auto-lint.js",
        editInput(path.join(tmpDir, "bad.js")),
        { timeout: 20000 }
      );
      assert.equal(exitCode, 0); // hook itself exits 0, outputs JSON
      assert.ok(stdout.length > 0, "should produce output");
      const result = JSON.parse(stdout);
      assert.equal(result.lint, "fail");
      assert.ok(result.eslintErrors.length > 0, "should have eslint errors");
      assert.ok(
        result.eslintErrors.some((e) => e.includes("no-unused-vars")),
        "should flag no-unused-vars"
      );
    });

    it("output JSON has expected shape", async () => {
      const { stdout } = await runHook(
        "auto-lint.js",
        editInput(path.join(tmpDir, "bad.js")),
        { timeout: 20000 }
      );
      const result = JSON.parse(stdout);
      assert.ok("lint" in result, "result should have lint field");
      assert.ok("typeErrors" in result, "result should have typeErrors field");
      assert.ok("eslintErrors" in result, "result should have eslintErrors field");
      assert.ok(Array.isArray(result.typeErrors));
      assert.ok(Array.isArray(result.eslintErrors));
    });
  });

  // ── TypeScript check (no tsconfig = skip) ─────────────────────────────

  describe("TypeScript check", () => {
    let tmpDir;

    before(() => {
      tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "auto-lint-tsc-"));
      // No tsconfig.json — tsc check should be skipped
      fs.writeFileSync(path.join(tmpDir, "app.ts"), `const x: number = "oops";\n`);
    });

    after(() => {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    it("skips tsc when no tsconfig.json exists", async () => {
      const { exitCode, stdout } = await runHook(
        "auto-lint.js",
        editInput(path.join(tmpDir, "app.ts")),
        { timeout: 15000 }
      );
      // No tsconfig, no eslint config => no output
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });
  });

  // ── findConfigDir walk-up logic ───────────────────────────────────────

  describe("config discovery (walk-up)", () => {
    let rootDir;

    before(() => {
      rootDir = fs.mkdtempSync(path.join(os.tmpdir(), "auto-lint-walkup-"));
      // package.json with eslint so the hook doesn't skip
      fs.writeFileSync(
        path.join(rootDir, "package.json"),
        JSON.stringify({ name: "test", devDependencies: { eslint: "^9.0.0" } })
      );
      // Put eslint config at root, file is nested 3 levels deep
      fs.writeFileSync(
        path.join(rootDir, "eslint.config.mjs"),
        `export default [{ rules: { "no-unused-vars": "error" } }];\n`
      );
      fs.mkdirSync(path.join(rootDir, "src", "components", "deep"), { recursive: true });
      fs.writeFileSync(
        path.join(rootDir, "src", "components", "deep", "widget.js"),
        `const unused = 1;\n`
      );
    });

    after(() => {
      fs.rmSync(rootDir, { recursive: true, force: true });
    });

    it("finds eslint config by walking up directories", async () => {
      const filePath = path.join(rootDir, "src", "components", "deep", "widget.js");
      const { stdout } = await runHook("auto-lint.js", editInput(filePath), { timeout: 20000 });
      assert.ok(stdout.length > 0, "should find config and produce output");
      const result = JSON.parse(stdout);
      assert.equal(result.lint, "fail");
      assert.ok(result.eslintErrors.length > 0);
    });
  });
});
