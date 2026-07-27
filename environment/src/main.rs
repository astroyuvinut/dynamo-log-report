use rusqlite::Connection;
use std::env;
use std::fs;
use std::path::Path;

const DB_PATH: &str = "/app/data.db";

fn get_conn() -> Connection {
    let conn = Connection::open(DB_PATH).expect("failed to open sqlite db");
    conn.execute(
        "CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, value INTEGER NOT NULL)",
        [],
    )
    .expect("failed to create table");
    conn
}

fn cmd_load(csv_path: &str) {
    let conn = get_conn();
    conn.execute("DELETE FROM records", []).expect("failed to clear table");

    let content = fs::read_to_string(Path::new(csv_path)).expect("failed to read input csv");
    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() {
            continue;
        }
        let value: i64 = line.parse().expect("expected one integer per line");
        conn.execute("INSERT INTO records (value) VALUES (?1)", [value])
            .expect("failed to insert record");
    }
    println!("LOADED");
}

fn cmd_stats_sum() {
    let conn = get_conn();
    // Deliberately uses a real SQL aggregate, not an in-Rust fold, so the
    // result can only come from a genuinely linked, functioning SQLite engine.
    let sum: i64 = conn
        .query_row("SELECT COALESCE(SUM(value), 0) FROM records", [], |row| row.get(0))
        .expect("failed to compute sum");
    println!("SUM={}", sum);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    match args.get(1).map(|s| s.as_str()) {
        Some("load") => {
            let csv_path = args.get(2).expect("usage: app load <csv_path>");
            cmd_load(csv_path);
        }
        Some("stats") if args.get(2).map(|s| s.as_str()) == Some("sum") => {
            cmd_stats_sum();
        }
        _ => {
            eprintln!("usage: app load <csv_path> | app stats sum");
            std::process::exit(2);
        }
    }
}
