"""
LEVEL 5 — Proof of Work dengan Nonce & Hash Blok Terintegrasi
=============================================================

Tujuan belajar:
  * Memahami Proof of Work yang mengikat isi blok ke hash blok menggunakan `nonce`.
  * Mengatasi kelemahan Level 3: perubahan data sekecil apa pun membatalkan hash blok.
  * Memahami mengapa serangan manipulasi data memerlukan penambangan ulang (re-mining)
    seluruh blok sesudahnya, yang membutuhkan kerja komputasi tinggi.
"""

import hashlib
import json


class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty
        self.chain = []
        # Buat blok genesis (index 0)
        genesis = {
            "index": 0,
            "transactions": [],
            "previous_hash": "0",
            "nonce": 0,
        }
        self.proof_of_work(genesis)
        self.chain.append(genesis)

    @staticmethod
    def hash_block(block: dict) -> str:
        """Kalkulasi hash SHA-256 dari blok secara kanonik, mengabaikan key 'hash' jika ada."""
        clean_block = {k: v for k, v in block.items() if k != "hash"}
        return hashlib.sha256(json.dumps(clean_block, sort_keys=True).encode()).hexdigest()

    def proof_of_work(self, block: dict) -> int:
        """Cari nonce terkecil mulai dari 0 sehingga hash blok diawali sejumlah `difficulty` angka '0'.
        
        Memperbarui field `nonce` dan `hash` pada dictionary blok secara in-place.
        Mengembalikan total percobaan (jumlah iterasi nonce).
        """
        target = "0" * self.difficulty
        nonce = 0
        percobaan = 0
        while True:
            block["nonce"] = nonce
            percobaan += 1
            h = self.hash_block(block)
            if h.startswith(target):
                block["hash"] = h
                return percobaan
            nonce += 1

    def new_block(self, transactions: list) -> dict:
        """Tambahkan blok baru ke rantai setelah ditambang melalui Proof of Work."""
        block = {
            "index": len(self.chain),
            "transactions": transactions,
            "previous_hash": self.chain[-1]["hash"],
            "nonce": 0,
        }
        self.proof_of_work(block)
        self.chain.append(block)
        return block

    def chain_valid(self) -> bool:
        """Validasi integritas seluruh blockchain:
        1. Hash setiap blok harus sama persis dengan kalkulasi hash_block(blok).
        2. Hash setiap blok harus memenuhi target difficulty.
        3. previous_hash setiap blok (mulai blok ke-1) harus sama dengan hash blok sebelumnya.
        """
        target = "0" * self.difficulty
        for i, block in enumerate(self.chain):
            # Periksa kecocokan hash tersimpan dengan isi blok
            if block.get("hash") != self.hash_block(block):
                return False

            # Periksa apakah hash memenuhi kriteria PoW
            if not str(block.get("hash", "")).startswith(target):
                return False

            # Periksa tautan previous_hash (kecuali blok genesis)
            if i > 0 and block.get("previous_hash") != self.chain[i - 1].get("hash"):
                return False

        return True

    def tambang_ulang_dari(self, mulai: int) -> int:
        """Tambang ulang seluruh blok mulai dari indeks `mulai` hingga akhir rantai.
        
        Setiap blok diperbarui `previous_hash`-nya dari hash blok sebelumnya, lalu
        dijalankan proof_of_work() untuk menemukan nonce dan hash baru.
        Mengembalikan total percobaan penambangan yang dilakukan.
        """
        total_usaha = 0
        for i in range(mulai, len(self.chain)):
            if i > 0:
                self.chain[i]["previous_hash"] = self.chain[i - 1]["hash"]
            usaha = self.proof_of_work(self.chain[i])
            total_usaha += usaha
        return total_usaha


if __name__ == "__main__":
    bc = Blockchain(difficulty=3)
    for tx in (["Ani->Budi 5"], ["Budi->Citra 2"], ["Citra->Dodi 1"]):
        b = bc.new_block(tx)
        print(f"Blok #{b['index']} ditambang, nonce={b['nonce']}, hash={b['hash']}")

    print("Rantai valid?", bc.chain_valid())

    # Contoh eksperimen pemalsuan
    print("\n-- Simulasi pemalsuan data pada blok 1 --")
    bc.chain[1]["transactions"] = ["Ani->Budi 500"]
    print("Setelah data diubah, valid?", bc.chain_valid())

    print("\n-- Menambang ulang dari blok 1 --")
    usaha = bc.tambang_ulang_dari(1)
    print(f"Selesai ditambang ulang ({usaha} percobaan). Valid?", bc.chain_valid())
