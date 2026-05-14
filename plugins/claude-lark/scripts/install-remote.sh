#!/usr/bin/env bash
#
# claude-lark one-line remote installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ysyecust/claude-lark/main/scripts/install-remote.sh | bash
#   curl ... | bash -s -- --phone 138xxxx
#   curl ... | bash -s -- --app-id cli_xxx --app-secret xxx --phone 138xxxx
#
set -euo pipefail

REPO_URL="https://github.com/ysyecust/claude-lark.git"
INSTALL_DIR="${CLAUDE_LARK_DIR:-$HOME/.claude-lark}"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

info()  { echo -e "${CYAN}[info]${NC}  $*"; }
ok()    { echo -e "${GREEN}  ✓${NC}   $*"; }
error() { echo -e "${RED}  ✗${NC}   $*"; exit 1; }

echo ""
echo -e "${BOLD}  claude-lark${NC} — One-Line Installer"
echo -e "  ─────────────────────────────────────"
echo ""

# ── Check dependencies ────────────────────────────────────────────────
command -v python3 &>/dev/null || error "python3 not found. Install Python 3.8+ first."
command -v git &>/dev/null || error "git not found. Install git first."
ok "python3 + git found"

# ── Clone or update ──────────────────────────────────────────────────
if [[ -d "$INSTALL_DIR/.git" ]]; then
    info "Updating existing installation at $INSTALL_DIR..."
    git -C "$INSTALL_DIR" pull --quiet origin main 2>/dev/null || true
    ok "Updated"
else
    info "Installing to $INSTALL_DIR..."
    git clone --quiet --depth 1 "$REPO_URL" "$INSTALL_DIR" 2>/dev/null
    ok "Cloned"
fi

# ── Run installer ────────────────────────────────────────────────────
chmod +x "$INSTALL_DIR/scripts/install.sh"
exec "$INSTALL_DIR/scripts/install.sh" "$@"
