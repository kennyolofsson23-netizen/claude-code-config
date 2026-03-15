const path = require("path");
const fs = require("fs");

let raw = "";
try {
  raw = fs.readFileSync(0, "utf8");
} catch (_) {}
const data = JSON.parse(raw || "{}");
const toolInput = data.tool_input || {};
const filePath = toolInput.file_path || toolInput.filePath || "";

if (!filePath.endsWith(".md")) {
  console.log(JSON.stringify({ allowed: true }));
  process.exit(0);
}

const allowedPatterns = [
  "/docs/",
  "/documentation/",
  "CLAUDE.md",
  "AGENTS.md",
  "CHANGELOG.md",
  "CODEMAP.md",
  "CONTRIBUTING.md",
  "SKILL.md",
  "/commands/",
  "/skills/",
  "/agents/",
  "/rules/",
  "/templates/",
  "\\docs\\",
  "\\documentation\\",
  "\\commands\\",
  "\\skills\\",
  "\\agents\\",
  "\\rules\\",
  "\\templates\\",
];

const isAllowed = allowedPatterns.some((pattern) => filePath.includes(pattern));

if (!isAllowed) {
  const fileName = path.basename(filePath);
  console.log(
    JSON.stringify({
      warning: `Creating ${fileName} outside of standard documentation directories. Make sure this file is intentional and not auto-generated boilerplate.`,
      file: filePath,
    })
  );
} else {
  console.log(JSON.stringify({ allowed: true }));
}
