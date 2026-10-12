import base64
from Crypto.Cipher import AES, ChaCha20
from Crypto.Util.Padding import pad, unpad

class CryptoEngine:

    # --- MENU 1: CAESAR CIPHER ---
    @staticmethod
    def caesar_encrypt(text: str, shift: int = 3):
        result = ""
        log = [f"Plaintext: '{text}' | Shift: {shift}"]
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += char
        log.append(f"Result (Caesar): {result}")
        return result, log

    @staticmethod
    def caesar_decrypt(ciphertext: str, shift: int = 3):
        return CryptoEngine.caesar_encrypt(ciphertext, -shift)

    # --- MENU 2: VIGENÈRE CIPHER ---
    @staticmethod
    def vigenere_encrypt(text: str, key: str = "TPS"):
        result = ""
        log = [f"Plaintext: '{text}' | Key: '{key}'"]
        key_clean = [c.upper() for c in key if c.isalpha()] or ['K']
        k_len = len(key_clean)
        k_idx = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                k_shift = ord(key_clean[k_idx % k_len]) - ord('A')
                result += chr((ord(char) - base + k_shift) % 26 + base)
                k_idx += 1
            else:
                result += char
        log.append(f"Result (Vigenere): {result}")
        return result, log

    @staticmethod
    def vigenere_decrypt(ciphertext: str, key: str = "TPS"):
        result = ""
        key_clean = [c.upper() for c in key if c.isalpha()] or ['K']
        k_len = len(key_clean)
        k_idx = 0
        
        for char in ciphertext:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                k_shift = ord(key_clean[k_idx % k_len]) - ord('A')
                result += chr((ord(char) - base - k_shift) % 26 + base)
                k_idx += 1
            else:
                result += char
        return result

    # --- MENU 3: AES-128 ---
    @staticmethod
    def aes_encrypt(text: str, key: str = "1234567890123456"): # Key 16 byte
        log = [f"AES-128 CBC Encrypt | Plaintext: '{text}'"]
        k_bytes = key.encode('utf-8')[:16].ljust(16, b'0')
        cipher = AES.new(k_bytes, AES.MODE_CBC)
        padded = pad(text.encode('utf-8'), AES.block_size)
        payload = cipher.iv + cipher.encrypt(padded)
        result = base64.b64encode(payload).decode('utf-8')
        log.append(f"Result (AES Base64): {result}")
        return result, log

    @staticmethod
    def aes_decrypt(encoded_text: str, key: str = "1234567890123456"):
        k_bytes = key.encode('utf-8')[:16].ljust(16, b'0')
        raw = base64.b64decode(encoded_text)
        cipher = AES.new(k_bytes, AES.MODE_CBC, iv=raw[:16])
        return unpad(cipher.decrypt(raw[16:]), AES.block_size).decode('utf-8')

    # --- MENU 4: CHACHA20 (FIXED 32-BYTE KEY) ---
    @staticmethod
    def chacha20_encrypt(text: str, key: str = "12345678901234567890123456789012"): # Key di-adjust jadi 32 byte
        log = [f"ChaCha20 Encrypt | Plaintext: '{text}'"]
        # Wajib 32 byte (256-bit)
        k_bytes = key.encode('utf-8')[:32].ljust(32, b'0')
        cipher = ChaCha20.new(key=k_bytes)
        payload = cipher.nonce + cipher.encrypt(text.encode('utf-8'))
        result = base64.b64encode(payload).decode('utf-8')
        log.append(f"Result (ChaCha20 Base64): {result}")
        return result, log

    @staticmethod
    def chacha20_decrypt(encoded_text: str, key: str = "12345678901234567890123456789012"):
        k_bytes = key.encode('utf-8')[:32].ljust(32, b'0')
        raw = base64.b64decode(encoded_text)
        cipher = ChaCha20.new(key=k_bytes, nonce=raw[:8])
        return cipher.decrypt(raw[8:]).decode('utf-8')

    # --- MENU 5: SUPER ENKRIPSI (4 Layer) ---
    @staticmethod
    def super_encrypt(text: str):
        logs = ["=== MULAI SUPER ENKRIPSI (MENU 5) ==="]
        s1, l1 = CryptoEngine.caesar_encrypt(text, 5)
        logs.extend(["[L1 Caesar]", *l1])
        
        s2, l2 = CryptoEngine.vigenere_encrypt(s1, "KPU")
        logs.extend(["[L2 Vigenere]", *l2])
        
        # Key ChaCha20 menggunakan string 32 byte
        s3, l3 = CryptoEngine.chacha20_encrypt(s2, "CHACHA20KEYMUSTBEEXACTLY32BYTES!")
        logs.extend(["[L3 ChaCha20]", *l3])
        
        final, l4 = CryptoEngine.aes_encrypt(s3, "AESKEYSUPER12345")
        logs.extend(["[L4 AES-128]", *l4])
        logs.append("=== SUPER ENKRIPSI SELESAI ===")
        return final, logs

    @staticmethod
    def super_decrypt(super_cipher: str):
        s3 = CryptoEngine.aes_decrypt(super_cipher, "AESKEYSUPER12345")
        s2 = CryptoEngine.chacha20_decrypt(s3, "CHACHA20KEYMUSTBEEXACTLY32BYTES!")
        s1 = CryptoEngine.vigenere_decrypt(s2, "KPU")
        original = CryptoEngine.caesar_decrypt(s1, 5)[0]
        return original