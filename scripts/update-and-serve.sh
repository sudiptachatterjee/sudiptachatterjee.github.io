#!/bin/bash
#
# update-and-serve.sh - Update reading section and preview/push changes
#
# Usage:
#   ./update-and-serve.sh          # Update and serve locally
#   ./update-and-serve.sh --push   # Update, serve, then commit and push

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PUSH_FLAG="$1"

# Run the Python update script
echo "Updating reading section..."
python3 "$SCRIPT_DIR/update-reading.py"

echo ""
echo "Starting local server at http://localhost:3000"
echo "Press Ctrl+C to stop the server and continue..."
echo ""

# Start the server in background, redirect output to hide noise
cd "$ROOT_DIR"
npx serve -l 3000 > /dev/null 2>&1 &
SERVER_PID=$!

# Trap Ctrl+C to stop server but continue script
trap "kill $SERVER_PID 2>/dev/null; wait $SERVER_PID 2>/dev/null; echo ''; echo 'Server stopped.'" INT

# Wait for server process (will be interrupted by Ctrl+C)
wait $SERVER_PID 2>/dev/null || true

# Reset trap
trap - INT

# If --push flag was provided, handle git operations
if [[ "$PUSH_FLAG" == "--push" ]]; then
    echo ""
    echo "=== Git Push ==="

    # Show what changed
    echo "Changes to be committed:"
    git -C "$ROOT_DIR" diff --stat
    echo ""

    # Ask for commit message
    read -p "Enter commit message: " commit_msg

    if [[ -z "$commit_msg" ]]; then
        echo "Error: Commit message cannot be empty"
        exit 1
    fi

    # Confirm before pushing
    echo ""
    echo "Will commit with message: \"$commit_msg\""
    read -p "Push to remote? (y/N): " confirm

    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        cd "$ROOT_DIR"
        git add .
        git commit -m "$commit_msg"
        git push
        echo "Pushed successfully!"
    else
        echo "Aborted."
    fi
fi
