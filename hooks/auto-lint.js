/**
 * PostToolUse hook: auto-lint on Edit/Write for TS/JS files.
 * Runs TypeScript type-checking (tsc --noEmit) and ESLint after every file edit.
 * Pipeline agents see errors immediately at edit-time, not at review time.
 */
const { execFileSync } = require("child_process");
const path = require("path");
const fs = require("fs");

// Read stdin JSON from Claude hook system
let raw = "";
try {
  raw = fs.readFileSync(0, "utf8");
} catch (_) {}
const data = JSON.parse(raw || "{}");
const toolInput = data.tool_input || {};
const filePath = toolInput.file_path || toolInput.filePath || "";
if (!filePath) process.exit(0);

// Only lint TS/JS files
const ext = path.extname(filePath).toLowerCase();
if (![".ts", ".tsx", ".js", ".jsx"].includes(ext)) process.exit(0);

const NPX = process.platform === "win32" ? "npx.cmd" : "npx";
const TIMEOUT = 15000;

/**
 * Walk up directories to find a config file matching any of the given patterns.
 * Returns the directory containing the config, or null.
 */
function findConfigDir(startDir, patterns, maxLevels = 15) {
  let dir = startDir;
  for (let i = 0; i < maxLevels; i++) {
    for (const pattern of patterns) {
      // Support glob-style prefix matching (e.g. ".eslintrc*")
      if (pattern.endsWith("*")) {
        const prefix = pattern.slice(0, -1);
        try {
          const entries = fs.readdirSync(dir);
          if (entries.some((e) => e.startsWith(prefix))) return dir;
        } catch (_) {}
      } else if (fs.existsSync(path.join(dir, pattern))) {
        return dir;
      }
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

const fileDir = path.dirname(filePath);
const result = { lint: "pass", typeErrors: [], eslintErrors: [] };

// ── TypeScript check ──────────────────────────────────────────────────────
const tsconfigDir = findConfigDir(fileDir, ["tsconfig.json"]);
if (tsconfigDir) {
  try {
    execFileSync(NPX, ["tsc", "--noEmit", "--pretty"], {
      cwd: tsconfigDir,
      stdio: "pipe",
      timeout: TIMEOUT,
      shell: true,
    });
  } catch (e) {
    const stderr = (e.stdout || e.stderr || "").toString();
    // Parse tsc output — each error line looks like: src/file.ts(10,5): error TS2322: ...
    const lines = stderr.split("\n").filter((l) => /error TS\d+/.test(l));
    // Only include errors relevant to the edited file
    const fileName = path.basename(filePath);
    const relevant = lines.filter((l) => l.includes(fileName));
    if (relevant.length > 0) {
      result.typeErrors = relevant.slice(0, 10).map((l) => l.trim());
      result.lint = "fail";
    } else if (lines.length > 0) {
      // Other files have errors — report count but don't fail this file
      result.typeErrors = [`${lines.length} type error(s) in project (not in edited file)`];
    }
  }
}

// ── ESLint check ──────────────────────────────────────────────────────────
const eslintDir = findConfigDir(fileDir, [
  ".eslintrc*",
  "eslint.config.js",
  "eslint.config.mjs",
  "eslint.config.cjs",
  "eslint.config.ts",
]);
if (eslintDir) {
  try {
    execFileSync(NPX, ["eslint", "--no-warn-ignored", filePath], {
      cwd: eslintDir,
      stdio: "pipe",
      timeout: TIMEOUT,
      shell: true,
    });
  } catch (e) {
    const output = (e.stdout || e.stderr || "").toString();
    const errorLines = output
      .split("\n")
      .filter((l) => /\d+:\d+\s+(error|warning)/.test(l))
      .slice(0, 10)
      .map((l) => l.trim());
    if (errorLines.length > 0) {
      result.eslintErrors = errorLines;
      // Only fail on actual errors, not warnings
      if (errorLines.some((l) => /\d+:\d+\s+error/.test(l))) {
        result.lint = "fail";
      }
    }
  }
}

// Only output if there's something to report
if (result.typeErrors.length > 0 || result.eslintErrors.length > 0) {
  console.log(JSON.stringify(result));
}
