const { execFileSync } = require("child_process");
const path = require("path");
const fs = require("fs");

let raw = "";
try {
  raw = fs.readFileSync(0, "utf8");
} catch (_) {}
const data = JSON.parse(raw || "{}");
const toolInput = data.tool_input || {};
const filePath = toolInput.file_path || toolInput.filePath || "";
if (!filePath) process.exit(0);

const ext = path.extname(filePath).toLowerCase();
if (![".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs"].includes(ext)) process.exit(0);

const dir = path.dirname(filePath);
const base = path.basename(filePath, ext);
const testPatterns = [
  path.join(dir, `${base}.test${ext}`),
  path.join(dir, `${base}.spec${ext}`),
  path.join(dir, "__tests__", `${base}.test${ext}`),
  path.join(dir, "__tests__", `${base}${ext}`),
  path.join(dir.replace("/src/", "/tests/"), `test_${base}.py`),
  path.join(dir.replace("\\src\\", "\\tests\\"), `test_${base}.py`),
];

const testFile = testPatterns.find((p) => fs.existsSync(p));
if (!testFile) process.exit(0);

const runners = {
  ".ts": { cmd: "npx", args: ["vitest", "run", testFile, "--reporter=verbose"] },
  ".tsx": { cmd: "npx", args: ["vitest", "run", testFile, "--reporter=verbose"] },
  ".js": { cmd: "npx", args: ["jest", "--testPathPattern", testFile, "--no-coverage"] },
  ".jsx": { cmd: "npx", args: ["jest", "--testPathPattern", testFile, "--no-coverage"] },
  ".py": { cmd: "python", args: ["-m", "pytest", testFile, "-x", "-q"] },
  ".go": { cmd: "go", args: ["test", "-run", "", "-v", dir] },
  ".rs": { cmd: "cargo", args: ["test", "--quiet"] },
};

const runner = runners[ext];

// Check if the test runner is available in the project before running
// This prevents noisy failures when vitest/jest/pytest aren't installed
function isRunnerAvailable(cmd, cwd) {
  // For npx-based runners, check if the package exists in node_modules or package.json
  if (cmd === "npx") {
    const pkgJsonPath = path.join(cwd, "package.json");
    if (!fs.existsSync(pkgJsonPath)) return false;
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgJsonPath, "utf8"));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };
      // Check for vitest or jest depending on runner args
      const runnerName = runner.args[0]; // "vitest" or "jest"
      return !!deps[runnerName];
    } catch (_) {
      return false;
    }
  }
  // For python/go/rs, just check if the command exists
  try {
    execFileSync(process.platform === "win32" ? "where" : "which", [cmd], {
      stdio: "pipe",
      timeout: 3000,
    });
    return true;
  } catch (_) {
    return false;
  }
}

// Find project root (nearest package.json or git root)
let projectRoot = process.cwd();
let checkDir = dir;
for (let i = 0; i < 10; i++) {
  if (fs.existsSync(path.join(checkDir, "package.json"))) {
    projectRoot = checkDir;
    break;
  }
  const parent = path.dirname(checkDir);
  if (parent === checkDir) break;
  checkDir = parent;
}

if (!isRunnerAvailable(runner.cmd, projectRoot)) {
  // Silently skip — runner not installed in this project
  process.exit(0);
}

try {
  const output = execFileSync(runner.cmd, runner.args, {
    stdio: "pipe",
    timeout: 30000,
    cwd: projectRoot,
    shell: true,
  });
  console.log(JSON.stringify({ tests: "pass", file: testFile, output: output.toString().slice(-300) }));
} catch (e) {
  const stderr = (e.stderr || e.stdout || "").toString().slice(0, 500);
  console.log(JSON.stringify({ tests: "fail", file: testFile, output: stderr }));
}
