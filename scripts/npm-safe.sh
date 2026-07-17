#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
VSCODE_NODE="$(find "$HOME/.vscode-server/bin" -maxdepth 2 -type f -name node 2>/dev/null | head -n 1 || true)"

run_real_npm() {
    timeout 10 npm --version >/dev/null 2>&1
}

if run_real_npm; then
    exec npm "$@"
fi

NODE_BIN="${NODE_BIN:-$VSCODE_NODE}"
if [ -z "$NODE_BIN" ] || [ ! -x "$NODE_BIN" ]; then
    echo "[错误] npm 不可用，且未找到可用的 Linux node。请修复 PATH 或设置 NODE_BIN。" >&2
    exit 127
fi

if [ "$#" -ge 3 ] && [ "$1" = "--prefix" ] && [ "$2" = "frontend" ] && [ "$3" = "run" ]; then
    SCRIPT_NAME="${4:-}"
    case "$SCRIPT_NAME" in
        type-check)
            cd "$FRONTEND_DIR"
            exec "$NODE_BIN" "$FRONTEND_DIR/node_modules/vue-tsc/bin/vue-tsc.js" --noEmit
            ;;
        build)
            cd "$FRONTEND_DIR"
            "$NODE_BIN" "$FRONTEND_DIR/node_modules/vue-tsc/bin/vue-tsc.js" --noEmit
            exec "$NODE_BIN" "$FRONTEND_DIR/node_modules/vite/bin/vite.js" build
            ;;
    esac
fi

if [ "$#" -ge 2 ] && [ "$1" = "run" ]; then
    case "$2" in
        type-check)
            cd "$FRONTEND_DIR"
            exec "$NODE_BIN" "$FRONTEND_DIR/node_modules/vue-tsc/bin/vue-tsc.js" --noEmit
            ;;
        build)
            cd "$FRONTEND_DIR"
            "$NODE_BIN" "$FRONTEND_DIR/node_modules/vue-tsc/bin/vue-tsc.js" --noEmit
            exec "$NODE_BIN" "$FRONTEND_DIR/node_modules/vite/bin/vite.js" build
            ;;
    esac
fi

echo "[错误] 当前 npm 不可用，无法执行: npm $*" >&2
echo "      已支持的兜底命令: run type-check / run build。" >&2
exit 127
