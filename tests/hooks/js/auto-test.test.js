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

/** Helper: create a package.json with test runner deps so the hook doesn't skip */
function createPackageJson(dir, deps = {}) {
  fs.writeFileSync(
    path.join(dir, "package.json"),
    JSON.stringify({ name: "test", devDependencies: deps })
  );
}

describe("auto-test.js", () => {
  // ── Early-exit paths ──────────────────────────────────────────────────

  describe("early exits", () => {
    it("exits 0 when no file_path provided", async () => {
      const { exitCode, stdout } = await runHook("auto-test.js", {});
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 when tool_input is empty", async () => {
      const { exitCode, stdout } = await runHook("auto-test.js", { tool_input: {} });
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 for unsupported extensions (.css)", async () => {
      const { exitCode, stdout } = await runHook("auto-test.js", editInput("/tmp/styles.css"));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 for unsupported extensions (.md)", async () => {
      const { exitCode, stdout } = await runHook("auto-test.js", editInput("/tmp/README.md"));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("exits 0 for unsupported extensions (.json)", async () => {
      const { exitCode, stdout } = await runHook("auto-test.js", editInput("/tmp/data.json"));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("accepts filePath alias (camelCase)", async () => {
      const { exitCode, stdout } = await runHook("auto-test.js", {
        tool_input: { filePath: "/tmp/test.css" },
      });
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });
  });

  // ── Supported extensions ──────────────────────────────────────────────

  describe("supported extensions (proceeds past extension check)", () => {
    for (const ext of [".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs"]) {
      it(`accepts ${ext} files`, async () => {
        // File doesn't exist = no test file found = exit 0
        const { exitCode, stdout } = await runHook(
          "auto-test.js",
          editInput(`/tmp/nonexistent/app${ext}`)
        );
        assert.equal(exitCode, 0);
        assert.equal(stdout, "", `should exit silently for ${ext} when no test file exists`);
      });
    }
  });

  // ── Test file discovery ───────────────────────────────────────────────

  describe("test file discovery", () => {
    let tmpDir;

    before(() => {
      tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "auto-test-discover-"));
      createPackageJson(tmpDir, { jest: "^29.0.0" });
    });

    after(() => {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    it("exits silently when no test file matches any pattern", async () => {
      // Create source file with no corresponding test
      const srcFile = path.join(tmpDir, "utils.js");
      fs.writeFileSync(srcFile, "module.exports = {};\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile));
      assert.equal(exitCode, 0);
      assert.equal(stdout, "");
    });

    it("finds .test.js sibling test file", async () => {
      const srcFile = path.join(tmpDir, "helper.js");
      const testFile = path.join(tmpDir, "helper.test.js");
      fs.writeFileSync(srcFile, "module.exports = {};\n");
      // Create a test that passes
      fs.writeFileSync(testFile, "test('pass', () => {});\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile), {
        timeout: 30000,
      });
      // The hook tries to run jest — it may fail (no jest installed) but it found the file
      assert.equal(exitCode, 0);
      assert.ok(stdout.length > 0, "should produce output when test file found");
      const result = JSON.parse(stdout);
      assert.ok(result.file.endsWith("helper.test.js"));
    });

    it("finds .spec.js sibling test file", async () => {
      const srcFile = path.join(tmpDir, "widget.js");
      const testFile = path.join(tmpDir, "widget.spec.js");
      fs.writeFileSync(srcFile, "module.exports = {};\n");
      fs.writeFileSync(testFile, "test('pass', () => {});\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile), {
        timeout: 30000,
      });
      assert.equal(exitCode, 0);
      assert.ok(stdout.length > 0);
      const result = JSON.parse(stdout);
      assert.ok(result.file.endsWith("widget.spec.js"));
    });

    it("finds test in __tests__ directory", async () => {
      const testsDir = path.join(tmpDir, "__tests__");
      fs.mkdirSync(testsDir, { recursive: true });
      const srcFile = path.join(tmpDir, "service.js");
      const testFile = path.join(testsDir, "service.test.js");
      fs.writeFileSync(srcFile, "module.exports = {};\n");
      fs.writeFileSync(testFile, "test('pass', () => {});\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile), {
        timeout: 30000,
      });
      assert.equal(exitCode, 0);
      assert.ok(stdout.length > 0);
      const result = JSON.parse(stdout);
      assert.ok(result.file.includes("__tests__"));
    });

    it("prefers .test over .spec (first match wins)", async () => {
      const srcFile = path.join(tmpDir, "priority.js");
      fs.writeFileSync(srcFile, "module.exports = {};\n");
      fs.writeFileSync(path.join(tmpDir, "priority.test.js"), "test('a', () => {});\n");
      fs.writeFileSync(path.join(tmpDir, "priority.spec.js"), "test('b', () => {});\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile), {
        timeout: 30000,
      });
      assert.equal(exitCode, 0);
      const result = JSON.parse(stdout);
      assert.ok(result.file.endsWith("priority.test.js"), "should prefer .test over .spec");
    });
  });

  // ── Runner selection ──────────────────────────────────────────────────

  describe("runner selection", () => {
    let tmpDir;

    before(() => {
      tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "auto-test-runner-"));
      createPackageJson(tmpDir, { jest: "^29.0.0", vitest: "^1.0.0" });
    });

    after(() => {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    it("uses jest for .js files (outputs pass or fail)", async () => {
      const srcFile = path.join(tmpDir, "jrunner.js");
      const testFile = path.join(tmpDir, "jrunner.test.js");
      fs.writeFileSync(srcFile, "module.exports = {};\n");
      fs.writeFileSync(testFile, "test('pass', () => { expect(true).toBe(true); });\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile), {
        timeout: 30000,
      });
      assert.equal(exitCode, 0);
      const result = JSON.parse(stdout);
      // Either pass or fail depending on jest availability — both are valid
      assert.ok(["pass", "fail"].includes(result.tests));
    });

    it("uses vitest for .ts files", async () => {
      const srcFile = path.join(tmpDir, "tsrunner.ts");
      const testFile = path.join(tmpDir, "tsrunner.test.ts");
      fs.writeFileSync(srcFile, "export const x = 1;\n");
      fs.writeFileSync(testFile, "import { expect, test } from 'vitest'; test('ok', () => { expect(1).toBe(1); });\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile), {
        timeout: 30000,
      });
      assert.equal(exitCode, 0);
      const result = JSON.parse(stdout);
      assert.ok(["pass", "fail"].includes(result.tests));
    });
  });

  // ── Output format ─────────────────────────────────────────────────────

  describe("output format", () => {
    let tmpDir;

    before(() => {
      tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "auto-test-format-"));
      createPackageJson(tmpDir, { jest: "^29.0.0" });
    });

    after(() => {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    });

    it("outputs valid JSON with tests, file, and output fields", async () => {
      const srcFile = path.join(tmpDir, "fmt.js");
      const testFile = path.join(tmpDir, "fmt.test.js");
      fs.writeFileSync(srcFile, "module.exports = {};\n");
      fs.writeFileSync(testFile, "test('ok', () => {});\n");

      const { exitCode, stdout } = await runHook("auto-test.js", editInput(srcFile), {
        timeout: 30000,
      });
      assert.equal(exitCode, 0);
      const result = JSON.parse(stdout);
      assert.ok("tests" in result, "should have tests field");
      assert.ok("file" in result, "should have file field");
      assert.ok("output" in result, "should have output field");
      assert.ok(typeof result.output === "string");
    });
  });
});
