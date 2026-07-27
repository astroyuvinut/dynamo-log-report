FROM rust:1.85-slim@sha256:9f841bbe9e7d8e37ceb96ed907265a3a0df7f44e3737d0b100e7907a679acb36

# Cross-toolchains for all four targets, plus QEMU user-mode + binfmt for
# executing aarch64/armv7 binaries, and Wine for the windows-gnu target.
# All installed at build time; the verifier itself runs with no network.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-aarch64-linux-gnu=4:12.2.0-3 \
    libc6-dev-arm64-cross=2.36-8cross1 \
    gcc-arm-linux-gnueabihf=4:12.2.0-3 \
    libc6-dev-armhf-cross=2.36-8cross1 \
    g++-mingw-w64-x86-64=12.2.0-14+25.2 \
    mingw-w64=10.0.0-3 \
    qemu-user-static=1:7.2+dfsg-7+deb12u18+b3 \
    wine=8.0~repack-4 \
    pkg-config \
    ca-certificates \
    python3=3.11.2-1+b1 \
    python3-pip=23.0.1+dfsg-1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.5

# qemu-*-static resolves the target's dynamic linker/libc at the standard
# multiarch paths (/lib/ld-linux-*, /usr/lib/<triplet>/*.so). The cross
# libc packages only ship those files under /usr/<triplet>/lib, so expose
# them at the paths qemu actually looks for.
RUN ln -s /usr/aarch64-linux-gnu/lib/ld-linux-aarch64.so.1 /lib/ld-linux-aarch64.so.1 \
    && ln -s /usr/arm-linux-gnueabihf/lib/ld-linux-armhf.so.3 /lib/ld-linux-armhf.so.3 \
    && for f in /usr/aarch64-linux-gnu/lib/*.so*; do ln -s "$f" /usr/lib/aarch64-linux-gnu/; done \
    && for f in /usr/arm-linux-gnueabihf/lib/*.so*; do ln -s "$f" /usr/lib/arm-linux-gnueabihf/; done

# Debian bookworm ships Wine 8.0, but Rust's getrandom has required
# bcryptprimitives.dll!ProcessPrng since Rust 1.76, and Wine didn't add
# that DLL until 8.13. Provide a minimal native stub forwarding to the
# RtlGenRandom implementation Wine already has, so the windows-gnu binary
# can actually run instead of failing to load.
RUN printf '#include <windows.h>\n\ntypedef BOOLEAN (WINAPI *RtlGenRandom_t)(PVOID, ULONG);\n\n__declspec(dllexport) BOOL WINAPI ProcessPrng(BYTE *pbData, SIZE_T cbData) {\n    HMODULE adv = LoadLibraryA("advapi32.dll");\n    if (!adv) return FALSE;\n    RtlGenRandom_t fn = (RtlGenRandom_t)GetProcAddress(adv, "SystemFunction036");\n    if (!fn) return FALSE;\n    return fn(pbData, (ULONG)cbData) ? TRUE : FALSE;\n}\n\nBOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID reserved) { return TRUE; }\n' > /tmp/bcryptprimitives.c \
    && x86_64-w64-mingw32-gcc -shared -O2 -o /tmp/bcryptprimitives.dll /tmp/bcryptprimitives.c \
    && WINEDEBUG=-all wine wineboot --init \
    && cp /tmp/bcryptprimitives.dll /root/.wine/drive_c/windows/system32/bcryptprimitives.dll \
    && rm -f /tmp/bcryptprimitives.c /tmp/bcryptprimitives.dll
ENV WINEDLLOVERRIDES="bcryptprimitives=n"

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
