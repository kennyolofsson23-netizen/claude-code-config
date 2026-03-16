/**
 * PreToolUse hook: validates agent .md frontmatter schema on Write.
 *
 * Blocks (exit 2) on: missing required fields (name, model, tools),
 *   invalid model, invalid memory, JSON-array tools, empty tools.
 * Warns (exit 0 + stderr) on: missing description, name/filename mismatch.
 * Passes (exit 0) for: non-agent files, valid agents.
 */
const fs = require("fs");
const path = require("path");

let raw = "";
try {
  raw = fs.readFileSync(0, "utf8");
} catch (_) {}
const data = JSON.parse(raw || "{}");
const toolInput = data.tool_input || {};
const filePath = toolInput.file_path || toolInput.filePath || "";
const content = toolInput.content || "";

// Only validate .md files inside an agents/ directory
const normalizedPath = filePath.replace(/\\/g, "/");
const isAgentFile =
  normalizedPath.endsWith(".md") &&
  /\/agents\/[^/]+\.md$/.test(normalizedPath);

if (!isAgentFile) {
  process.exit(0);
}

// Extract frontmatter
const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
if (!fmMatch) {
  process.stderr.write("BLOCKED: Agent file missing YAML frontmatter (--- delimiters).\n");
  process.exit(2);
}

const fmRaw = fmMatch[1];

// Simple YAML parser for flat key-value + array fields
function parseFrontmatter(raw) {
  const result = {};
  const lines = raw.split(/\r?\n/);
  let currentKey = null;
  let currentArray = null;

  for (const line of lines) {
    // Array item: "  - value"
    const arrayItem = line.match(/^\s+-\s+(.+)$/);
    if (arrayItem && currentKey) {
      if (!currentArray) currentArray = [];
      currentArray.push(arrayItem[1].trim());
      continue;
    }

    // If we were collecting array items, save them
    if (currentArray && currentKey) {
      result[currentKey] = currentArray;
      currentArray = null;
    }

    // Key-value: "key: value"
    const kv = line.match(/^([a-zA-Z_]\w*)\s*:\s*(.*)$/);
    if (kv) {
      currentKey = kv[1];
      const value = kv[2].trim();

      if (value === "") {
        // Could be start of array or empty value
        currentArray = [];
      } else if (value.startsWith("[")) {
        // JSON-array inline — store as raw string to detect later
        result[currentKey] = { __jsonArray: true, raw: value };
      } else {
        result[currentKey] = value;
      }
    }
  }

  // Flush trailing array
  if (currentArray && currentKey) {
    result[currentKey] = currentArray;
  }

  return result;
}

const fm = parseFrontmatter(fmRaw);

const VALID_MODELS = ["sonnet", "opus", "haiku"];
const VALID_MEMORY = ["project", "user"];

const errors = [];
const warnings = [];

// Required: name
if (!fm.name) {
  errors.push("Missing required field: name");
}

// Required: model
if (!fm.model) {
  errors.push("Missing required field: model");
} else if (!VALID_MODELS.includes(fm.model)) {
  errors.push(`Invalid model "${fm.model}" — must be one of: ${VALID_MODELS.join(", ")}`);
}

// Required: tools (YAML array format)
if (!fm.tools) {
  errors.push("Missing required field: tools");
} else if (fm.tools.__jsonArray) {
  errors.push(
    'Tools must use YAML array format (- item), not JSON inline (["item"])'
  );
} else if (Array.isArray(fm.tools) && fm.tools.length === 0) {
  errors.push("Tools array is empty — at least one tool is required");
}

// Optional: memory validation
if (fm.memory && !VALID_MEMORY.includes(fm.memory)) {
  errors.push(
    `Invalid memory "${fm.memory}" — must be one of: ${VALID_MEMORY.join(", ")}`
  );
}

// Warning: missing description
if (!fm.description) {
  warnings.push("Missing recommended field: description");
}

// Warning: name/filename mismatch
if (fm.name) {
  const expectedName = path.basename(normalizedPath, ".md");
  if (fm.name !== expectedName) {
    warnings.push(
      `Name "${fm.name}" doesn't match filename "${expectedName}.md"`
    );
  }
}

// Block on errors
if (errors.length > 0) {
  process.stderr.write(
    `BLOCKED: Agent schema validation failed:\n${errors.map((e) => `  - ${e}`).join("\n")}\n`
  );
  process.exit(2);
}

// Warn but allow
if (warnings.length > 0) {
  process.stderr.write(
    `Agent schema warnings:\n${warnings.map((w) => `  - ${w}`).join("\n")}\n`
  );
}

process.exit(0);
