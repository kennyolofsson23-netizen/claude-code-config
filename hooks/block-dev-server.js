let raw = "";
try {
  raw = require("fs").readFileSync(0, "utf8");
} catch (_) {}
const data = JSON.parse(raw || "{}");
const toolInput = data.tool_input || {};
const command = (toolInput.command || "").toLowerCase();

const devServerPatterns = [
  "npm run dev",
  "npm start",
  "yarn dev",
  "pnpm dev",
  "bun dev",
  "next dev",
  "vite",
  "webpack serve",
  "nodemon",
  "ts-node-dev",
  "python manage.py runserver",
  "flask run",
  "uvicorn",
  "cargo watch",
];

const isDevServer = devServerPatterns.some((p) => command.includes(p));
if (!isDevServer) {
  console.log(JSON.stringify({ allowed: true }));
  process.exit(0);
}

const inTmux = !!process.env.TMUX;
const inScreen = !!process.env.STY;

if (!inTmux && !inScreen) {
  // Warn but don't block — beginners may not have tmux/screen installed
  process.stderr.write(
    "WARNING: Dev server commands can leave orphaned processes. Consider running inside tmux/screen or use run_in_background.\n"
  );
  process.exit(0);
}

console.log(JSON.stringify({ allowed: true, multiplexer: inTmux ? "tmux" : "screen" }));
