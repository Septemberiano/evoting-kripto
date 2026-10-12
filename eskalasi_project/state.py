import reflex as rx
import sqlite3
import hashlib
from typing import List, Dict
from .ciphers import CryptoEngine
from .db import DB_PATH

class State(rx.State):
    # --- Auth State ---
    username: str = ""
    password: str = ""
    logged_in: bool = False
    current_user_id: int = -1
    is_admin: bool = False
    auth_message: str = ""

    # --- Voting Form State ---
    nik_input: str = ""
    nama_input: str = ""
    tps_input: str = ""
    pilihan_kandidat: str = "Paslon 01 - Alice & Bob"
    has_voted: bool = False
    encryption_logs: List[str] = []

    # --- Management Lists (Admin & Voter) ---
    user_list: List[Dict[str, str]] = []
    tps_list: List[Dict[str, str]] = []
    kandidat_admin_list: List[Dict[str, str]] = []
    kandidat_options: List[str] = [
        "Paslon 01 - Alice & Bob",
        "Paslon 02 - Charlie & David"
    ]
    raw_votes_db: List[Dict[str, str]] = []
    decrypted_results: Dict[str, int] = {}
    is_decrypted: bool = False

    # --- Form Inputs Admin ---
    new_username: str = ""
    new_password: str = ""
    new_kode_tps: str = ""
    new_nama_tps: str = ""

    # --- Setter Methods ---
    def set_username(self, v: str): self.username = v
    def set_password(self, v: str): self.password = v
    def set_nik_input(self, v: str): self.nik_input = v
    def set_nama_input(self, v: str): self.nama_input = v
    def set_tps_input(self, v: str): self.tps_input = v
    def set_pilihan_kandidat(self, v: str): self.pilihan_kandidat = v
    def set_new_username(self, v: str): self.new_username = v
    def set_new_password(self, v: str): self.new_password = v
    def set_new_kode_tps(self, v: str): self.new_kode_tps = v
    def set_new_nama_tps(self, v: str): self.new_nama_tps = v

    # --- Auth Logic ---
    def login(self):
        if not self.username or not self.password:
            self.auth_message = "Username & Password wajib diisi!"
            return

        pass_hash = hashlib.sha256(self.password.encode()).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, password_hash FROM users WHERE username = ?", (self.username,))
        user = cursor.fetchone()

        if user:
            if user[2] == pass_hash:
                self.logged_in = True
                self.current_user_id = user[0]
                self.is_admin = (user[1] == "admin")
                self.auth_message = ""
                if self.is_admin:
                    self.fetch_admin_data()
                else:
                    cursor.execute("SELECT status_voted FROM dpt WHERE user_id = ?", (self.current_user_id,))
                    dpt = cursor.fetchone()
                    self.has_voted = bool(dpt and dpt[0] == 1)
                    self.fetch_kandidat()
            else:
                self.auth_message = "Password salah!"
        else:
            # Auto Register Voter
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'voter')", (self.username, pass_hash))
            conn.commit()
            self.logged_in = True
            self.current_user_id = cursor.lastrowid
            self.is_admin = False
            self.has_voted = False
            self.auth_message = ""
            self.fetch_kandidat()

        conn.close()

    def logout(self):
        self.logged_in = False
        self.is_admin = False
        self.username = ""
        self.password = ""
        self.auth_message = ""

    # --- CRUD ADMIN ---
    def add_user(self):
        if not self.new_username or not self.new_password: return
        p_hash = hashlib.sha256(self.new_password.encode()).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'voter')", (self.new_username, p_hash))
            conn.commit()
            self.new_username = ""
            self.new_password = ""
        except sqlite3.IntegrityError:
            pass
        conn.close()
        self.fetch_admin_data()

    def delete_user(self, user_id: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", (int(user_id),))
        conn.commit()
        conn.close()
        self.fetch_admin_data()

    def add_tps(self):
        if not self.new_kode_tps or not self.new_nama_tps: return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO master_tps (kode_tps, nama_lokasi) VALUES (?, ?)", (self.new_kode_tps, self.new_nama_tps))
            conn.commit()
            self.new_kode_tps = ""
            self.new_nama_tps = ""
        except sqlite3.IntegrityError:
            pass
        conn.close()
        self.fetch_admin_data()

    def delete_tps(self, tps_id: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM master_tps WHERE id = ?", (int(tps_id),))
        conn.commit()
        conn.close()
        self.fetch_admin_data()

    def fetch_admin_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, role, created_at FROM users")
        self.user_list = [{"id": str(r[0]), "username": r[1], "role": r[2], "created_at": str(r[3])} for r in cursor.fetchall()]
        
        cursor.execute("SELECT id, kode_tps, nama_lokasi FROM master_tps")
        self.tps_list = [{"id": str(r[0]), "kode": r[1], "nama": r[2]} for r in cursor.fetchall()]
        
        cursor.execute("SELECT id, nomor_urut, nama_paslon FROM kandidat")
        self.kandidat_admin_list = [{"id": str(r[0]), "no": str(r[1]), "nama": r[2]} for r in cursor.fetchall()]
        
        conn.close()

    def fetch_kandidat(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT nama_paslon FROM kandidat ORDER BY nomor_urut ASC")
        rows = cursor.fetchall()
        if rows:
            self.kandidat_options = [r[0] for r in rows]
        if self.kandidat_options and not self.pilihan_kandidat:
            self.pilihan_kandidat = self.kandidat_options[0]
        conn.close()

    # --- VOTING & DECRYPTION LOGIC ---
    def submit_vote(self):
        if not self.nik_input or not self.nama_input or not self.tps_input: return
        tps_enc, log1 = CryptoEngine.caesar_encrypt(self.tps_input, 3)
        nik_enc, log3 = CryptoEngine.aes_encrypt(self.nik_input)
        nama_enc, log4 = CryptoEngine.chacha20_encrypt(self.nama_input)
        pilihan_enc, super_log = CryptoEngine.super_encrypt(self.pilihan_kandidat)

        self.encryption_logs = log1 + log3 + log4 + super_log

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dpt (user_id, nik_encrypted, nama_encrypted, status_voted) 
            VALUES (?, ?, ?, 1) ON CONFLICT(user_id) DO UPDATE SET status_voted=1
        """, (self.current_user_id, nik_enc, nama_enc))
        cursor.execute("INSERT INTO votes (tps_encrypted, pilihan_super_encrypted) VALUES (?, ?)", (tps_enc, pilihan_enc))
        conn.commit()
        conn.close()
        self.has_voted = True

    def load_db_votes(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tps_encrypted, pilihan_super_encrypted, timestamp FROM votes")
        self.raw_votes_db = [{"id": str(r[0]), "tps": r[1], "pilihan": r[2], "time": r[3]} for r in cursor.fetchall()]
        conn.close()

    def decrypt_all_votes(self):
        self.load_db_votes()
        results = {}
        for vote in self.raw_votes_db:
            pt = CryptoEngine.super_decrypt(vote["pilihan"])
            results[pt] = results.get(pt, 0) + 1
        self.decrypted_results = results
        self.is_decrypted = True