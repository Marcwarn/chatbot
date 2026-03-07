#!/bin/bash
#
# Setup Script for Git Security Hooks
# Configures Git to use the security validation hooks
#

set -e

echo "🔒 Setting up Git Security Hooks..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if we're in a Git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Not in a Git repository${NC}"
    exit 1
fi

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.githooks"

echo -e "${BLUE}📁 Repository: $REPO_ROOT${NC}"
echo -e "${BLUE}🪝 Hooks directory: $HOOKS_DIR${NC}"
echo ""

# Check if hooks directory exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo -e "${RED}❌ ERROR: Hooks directory not found${NC}"
    echo "Expected: $HOOKS_DIR"
    exit 1
fi

# Step 1: Make hooks executable
echo "🔧 [1/4] Making hooks executable..."
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/commit-msg"
chmod +x "$HOOKS_DIR/pre-push"
echo -e "${GREEN}✅ Hooks are now executable${NC}"
echo ""

# Step 2: Configure Git to use custom hooks directory
echo "⚙️  [2/4] Configuring Git hooks path..."
git config core.hooksPath .githooks
echo -e "${GREEN}✅ Git hooks path configured${NC}"
echo ""

# Step 3: Verify configuration
echo "🔍 [3/4] Verifying configuration..."
HOOKS_PATH=$(git config core.hooksPath)
if [ "$HOOKS_PATH" = ".githooks" ]; then
    echo -e "${GREEN}✅ Configuration verified${NC}"
else
    echo -e "${RED}❌ ERROR: Configuration failed${NC}"
    exit 1
fi
echo ""

# Step 4: Test hooks
echo "🧪 [4/4] Testing hooks..."
if [ -x "$HOOKS_DIR/pre-commit" ] && [ -x "$HOOKS_DIR/commit-msg" ] && [ -x "$HOOKS_DIR/pre-push" ]; then
    echo -e "${GREEN}✅ All hooks are executable and ready${NC}"
else
    echo -e "${RED}❌ ERROR: Some hooks are not executable${NC}"
    exit 1
fi
echo ""

# Success summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Git security hooks successfully installed!${NC}"
echo ""
echo "Installed hooks:"
echo "  • pre-commit  - Validates code for security vulnerabilities before commit"
echo "  • commit-msg  - Ensures security commits are well-documented"
echo "  • pre-push    - Final production readiness checks before push"
echo ""
echo "Next steps:"
echo "  1. Read LESSONS_LEARNED.md to understand security best practices"
echo "  2. Review SECURITY_CHECKLIST.md before committing code"
echo "  3. Test the hooks with a dummy commit"
echo ""
echo "To test the pre-commit hook:"
echo "  echo 'password = \"test123\"' > test.py"
echo "  git add test.py"
echo "  git commit -m 'Test commit'"
echo "  # Should fail with hardcoded password error"
echo "  git reset HEAD test.py && rm test.py"
echo ""
echo "To temporarily disable hooks (NOT RECOMMENDED):"
echo "  git commit --no-verify  # Skip pre-commit and commit-msg"
echo "  git push --no-verify    # Skip pre-push"
echo ""
echo "To uninstall hooks:"
echo "  git config --unset core.hooksPath"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Never bypass hooks for production code!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
