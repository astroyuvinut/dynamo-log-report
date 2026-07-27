# TODO: this sandbox has no network access to Docker Hub, so I cannot
# resolve the real sha256 digest for rust:1.85-slim from here.
# On your machine, run:
#   docker pull rust:1.85-slim
#   docker inspect --format='{{index .RepoDigests 0}}' rust:1.85-slim
# and replace the digest below with the real one before submitting.
FROM rust:1.85-slim@sha256:REPLACE_WITH_REAL_DIGEST

# Cross-toolchains for all four targets, plus QEMU user-mode + binfmt for
# executing aarch64/armv7 binaries, and Wine for the windows-gnu target.
# All installed at build time; the verifier itself runs with no network.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-aarch64-linux-gnu=4:12.2.0-3 \
    gcc-arm-linux-gnueabihf=4:12.2.0-3 \
    g++-mingw-w64-x86-64=12.0.0-16 \
    mingw-w64=12.0.0-16 \
    qemu-user-static=1:7.2+dfsg-7+deb12u7 \
    wine=8.0.2-3 \
    pkg-config \
    ca-certificates \
    python3=3.11.2-1+b1 \
    python3-pip=23.0.1+dfsg-1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.5

RUN rustup target add \
    x86_64-unknown-linux-gnu \
    aarch64-unknown-linux-gnu \
    armv7-unknown-linux-gnueabihf \
    x86_64-pc-windows-gnu

WORKDIR /app
COPY . /app

# Pre-fetch all crate dependencies at build time so the agent's cargo build
# works with no network access at runtime (allow_internet = false).
RUN cargo fetch --target x86_64-unknown-linux-gnu \
    && cargo fetch --target aarch64-unknown-linux-gnu \
    && cargo fetch --target armv7-unknown-linux-gnueabihf \
    && cargo fetch --target x86_64-pc-windows-gnu

# No solution files are copied in — .cargo/config.toml here is the
# intentionally-incomplete starting state, and there is no solve.sh or
# oracle-fixed config baked into this image (it lives only under
# /solution, outside the agent's /app working directory).
