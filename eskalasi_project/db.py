import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'evoting.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Tabel Users (Kredensial & Role)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'voter')) NOT NULL DEFAULT 'voter',
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Tabel Master TPS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS master_tps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_tps TEXT UNIQUE NOT NULL,
            nama_lokasi TEXT NOT NULL,
            kuota_pemilih INTEGER DEFAULT 100
        )
    ''')

    # 3. Tabel Master Paslon / Kandidat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kandidat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_urut INTEGER UNIQUE NOT NULL,
            nama_paslon TEXT NOT NULL,
            visi_misi TEXT
        )
    ''')

    # 4. Tabel DPT (Data Pemilih Terenkripsi)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dpt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            tps_id INTEGER,
            nik_encrypted TEXT NOT NULL,
            nama_encrypted TEXT NOT NULL,
            status_voted INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (tps_id) REFERENCES master_tps(id)
        )
    ''')
    
    # 5. Tabel Votes (Kotak Suara Terenkripsi)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tps_encrypted TEXT NOT NULL,
            pilihan_super_encrypted TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert Default Admin jika belum ada
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        pass_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')", 
            ('admin', pass_hash)
        )
        print("[+] Account Admin Default Berhasil Dibuat (User: admin | Pass: admin123)")
        
    # Seed Default Paslon jika tabel masih kosong
    cursor.execute("SELECT COUNT(*) FROM kandidat")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO kandidat (nomor_urut, nama_paslon, visi_misi) VALUES (1, 'Paslon 01 - Alice & Bob', 'Keadilan Digital')")
        cursor.execute("INSERT INTO kandidat (nomor_urut, nama_paslon, visi_misi) VALUES (2, 'Paslon 02 - Charlie & David', 'Transparansi Kripto')")
        print("[+] Data Master Paslon Default Berhasil Dibuat")

    conn.commit()
    conn.close()
    print("[+] Inisialisasi Database & Tabel SQLite Selesai.")

if __name__ == "__main__":
    init_db()