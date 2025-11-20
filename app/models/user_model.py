from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"   # <-- perbaikan: double underscore

    # --- Kolom utama ---
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default="user")
    password_hash = db.Column(db.String(128), nullable=True)

    # --- Method untuk menyimpan password dalam bentuk hash ---
    def set_password(self, password: str):
        """Simpan password sebagai hash (jangan pernah simpan plaintext)."""
        self.password_hash = generate_password_hash(password)

    # --- Method untuk verifikasi password saat login ---
    def check_password(self, password: str) -> bool:
        """Cek apakah password cocok dengan hash yang tersimpan."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # cegah akses langsung ke password_hash sebagai atribut "password"
    @property
    def password(self):
        raise AttributeError("Password tidak bisa dibaca.")

    @password.setter
    def password(self, raw_password: str):
        # Biar bisa set pakai: user.password = "rahasia"
        self.set_password(raw_password)

    # --- Method untuk konversi data ke dictionary (tanpa password) ---
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "role": self.role
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"  # <-- perbaikan: double underscore
