There's a Rust CLI crate at /app. It has two subcommands: `load <csv_path>`, which reads a file of one integer per line into a local SQLite database, and `stats sum`, which prints the sum of all loaded values as `SUM=<total>`. The SQLite dependency (`rusqlite`, "bundled" feature) compiles its own C source rather than linking a system library.

We need release binaries for four targets:

1. x86_64-unknown-linux-gnu
2. aarch64-unknown-linux-gnu
3. armv7-unknown-linux-gnueabihf
4. x86_64-pc-windows-gnu

Right now only the first target builds and links successfully. Fix whatever is needed (toolchain/linker configuration, not application logic) so all four targets build, and so `stats sum` produces the correct sum on all four via the same code path — the SQLite-backed aggregate must work identically on every target, not be worked around or disabled for the ones that don't build out of the box.

Required output paths, one release binary per target:

1. /app/target/x86_64-unknown-linux-gnu/release/app
2. /app/target/aarch64-unknown-linux-gnu/release/app
3. /app/target/armv7-unknown-linux-gnueabihf/release/app
4. /app/target/x86_64-pc-windows-gnu/release/app.exe

Success criteria:

1. All four binaries exist at the paths above and are release builds for their respective target architecture/format.
2. Running `<binary> load /app/input.csv` followed by `<binary> stats sum` on each of the four binaries (via their respective platform's execution method) prints `SUM=<total>` where `<total>` is the correct integer sum of the values in /app/input.csv, computed via a real SQL query inside the binary.
3. No target achieves this by disabling, stubbing, or bypassing the SQLite-backed aggregate — all four must exercise the same `rusqlite`-backed code path.
