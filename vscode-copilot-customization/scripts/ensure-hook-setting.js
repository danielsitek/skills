#!/usr/bin/env node
/**
 * ensure-hook-setting.js
 *
 * Ensures that .vscode/settings.json contains:
 *   "chat.hookFilesLocations": { ".github/hooks": true }
 *
 * - Creates .vscode/settings.json if it doesn't exist.
 * - Adds the key if missing.
 * - Merges the value if the key exists but ".github/hooks" is absent.
 * - Does nothing if already configured correctly.
 *
 * Usage: node scripts/ensure-hook-setting.js [workspace-root]
 * Default workspace root: current working directory.
 */

const fs = require("node:fs");
const path = require("node:path");

const HOOK_SETTING_KEY = "chat.hookFilesLocations";
const HOOK_PATH = ".github/hooks";

const workspaceRoot = process.argv[2] || process.cwd();
const settingsDir = path.join(workspaceRoot, ".vscode");
const settingsFile = path.join(settingsDir, "settings.json");

function readSettings(filePath) {
  if (!fs.existsSync(filePath)) return {};
  const raw = fs.readFileSync(filePath, "utf8").trim();
  if (!raw) return {};
  // Strip single-line comments before parsing (VS Code allows them)
  const stripped = raw.replace(/\/\/[^\n]*/g, "");
  try {
    return JSON.parse(stripped);
  } catch {
    console.error(`❌  Could not parse ${filePath} — please check for syntax errors.`);
    process.exit(1);
  }
}

function writeSettings(filePath, settings) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(settings, null, 2) + "\n", "utf8");
}

const settings = readSettings(settingsFile);
const existing = settings[HOOK_SETTING_KEY];

if (existing && typeof existing === "object" && existing[HOOK_PATH] === true) {
  console.log(`✅  ${HOOK_SETTING_KEY} already configured — no changes needed.`);
  process.exit(0);
}

// Merge or create
settings[HOOK_SETTING_KEY] = Object.assign({}, existing || {}, {
  [HOOK_PATH]: true,
});

writeSettings(settingsFile, settings);
console.log(`✅  Added "${HOOK_PATH}": true to ${HOOK_SETTING_KEY} in .vscode/settings.json`);
