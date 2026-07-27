#!/usr/bin/env bash
set -euo pipefail
cd /app

# The fix: configure the missing cross-linkers. This is the one change
# that matters - everything else in the crate is already correct.
cat > .cargo/config.toml <<'EOF'
[target.x86_64-unknown-linux-gnu]
linker = "gcc"

[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"

[target.armv7-unknown-linux-gnueabihf]
linker = "arm-linux-gnueabihf-gcc"

[target.x86_64-pc-windows-gnu]
linker = "x86_64-w64-mingw32-gcc"
EOF

cargo build --release --target x86_64-unknown-linux-gnu
cargo build --release --target aarch64-unknown-linux-gnu
cargo build --release --target armv7-unknown-linux-gnueabihf
cargo build --release --target x86_64-pc-windows-gnu
