"""
LEVEL 4 — Transaksi & Mempool (Pending Transactions)
=====================================================

Tujuan belajar:
  * Memahami konsep transaksi dan daftar transaksi tertunda (pending transactions/mempool).
  * Validasi input transaksi (pengirim, penerima, jumlah).
  * Memasukkan transaksi yang tertunda ke dalam blok baru saat penambangan.
  * Menelusuri riwayat transaksi akun tertentu dalam rantai blok.
"""

import datetime
import hashlib
import json


class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty
        self.chain = []
        self.pending_transactions = []
        # Blok genesis (blok pertama)
        self.create_block(proof=1, previous_hash="0")

    def create_block(self, proof: int, previous_hash: str) -> dict:
        """Buat blok baru, masukkan pending_transactions, dan bersihkan antrean pending."""
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "transactions": list(self.pending_transactions),
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def last_block(self) -> dict:
        return self.chain[-1]

    def hash(self, block: dict) -> str:
        """SHA-256 dari blok yang diserialisasi JSON secara kanonik (sort_keys=True)."""
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def valid_proof(self, previous_proof: int, proof: int) -> bool:
        """True jika SHA-256(str(proof**2 - previous_proof**2)) diawali `difficulty` angka nol."""
        h = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
        return h.startswith("0" * self.difficulty)

    def proof_of_work(self, previous_proof: int) -> int:
        """Cari proof terkecil mulai dari 1 yang memenuhi valid_proof()."""
        proof = 1
        while not self.valid_proof(previous_proof, proof):
            proof += 1
        return proof

    def add_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """Tambahkan transaksi baru ke daftar pending_transactions.

        Validasi:
          - sender dan recipient harus berupa string dan tidak boleh kosong/whitespace.
          - sender tidak boleh sama dengan recipient.
          - amount harus berupa tipe data int atau float (bukan bool), dan bernilai > 0.

        Kembalikan index dari blok berikutnya yang akan memuat transaksi ini.
        """
        if not isinstance(sender, str) or not isinstance(recipient, str):
            raise ValueError("Sender dan recipient harus berupa string")

        if not sender.strip() or not recipient.strip():
            raise ValueError("Sender dan recipient tidak boleh kosong")

        if sender.strip() == recipient.strip():
            raise ValueError("Sender tidak boleh sama dengan recipient")

        # Di Python, bool merupakan subclass dari int, sehingga perlu dicek secara khusus
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Amount harus berupa tipe data angka (int atau float)")

        if amount <= 0:
            raise ValueError("Amount harus bernilai lebih besar dari 0")

        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        })
        return len(self.chain) + 1

    def mine_block(self) -> dict:
        """Tambang blok baru yang menyertakan seluruh transaksi pending saat ini."""
        prev_block = self.last_block()
        proof = self.proof_of_work(prev_block["proof"])
        prev_hash = self.hash(prev_block)
        return self.create_block(proof, prev_hash)

    def riwayat(self, nama: str) -> list:
        """Cari seluruh transaksi yang melibatkan `nama` (sebagai sender atau recipient)
        dalam blok yang sudah ditambang.

        Kembalikan list berisi tuple: (block_index, transaction_dict).
        """
        hasil = []
        for block in self.chain:
            for tx in block.get("transactions", []):
                if tx.get("sender") == nama or tx.get("recipient") == nama:
                    hasil.append((block["index"], tx))
        return hasil


if __name__ == "__main__":
    bc = Blockchain(difficulty=3)
    bc.add_transaction("Ani", "Budi", 5)
    bc.add_transaction("Budi", "Citra", 2.5)
    print("Pending transactions:", bc.pending_transactions)
    b = bc.mine_block()
    print(f"Blok #{b['index']} ditambang dengan {len(b['transactions'])} transaksi")
    print("Riwayat Budi:", bc.riwayat("Budi"))
