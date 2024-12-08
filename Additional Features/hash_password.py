import hashlib

# Password yang ingin di-hash
password = "123"

# Meng-hash password menggunakan SHA-256
hashed_password = hashlib.sha256(password.encode()).hexdigest()

print(f"Hashed Password: {hashed_password}")
