import sys
sys.path.append('.')

from app.utils.password_helper import verify_password

# Password hash từ database
username = 'johndoe'
password_hash = '$2b$12$E01bY53QJ5B70WEl.BcSLOyY6thM.4kSqJzwtKi21EIsb9M4FUabe'

# Test passwords
test_passwords = [
    'password123',
    'Password123',
    'password',
    '123456',
    'johndoe'
]

print("=" * 60)
print(f"🔐 Testing password hash for user: {username}")
print("=" * 60)
print(f"Hash: {password_hash}")
print("=" * 60)

for pwd in test_passwords:
    result = verify_password(pwd, password_hash)
    status = "✅ VALID" if result else "❌ INVALID"
    print(f"{status} - Password: '{pwd}'")

print("=" * 60)