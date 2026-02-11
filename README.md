# passwordmanager

A Unicode codepoint-based password manager that generates cryptographically secure passwords with 86+ bits of entropy.

## Overview

This password manager uses Unicode codepoints from various character sets to generate highly secure passwords. By leveraging the vast Unicode character space (2,797 carefully selected printable codepoints), each character provides approximately 11.45 bits of entropy.

### Key Features

- **High Entropy**: Generates passwords with 86+ bits of entropy by default (8 Unicode characters)
- **Cryptographically Secure**: Uses Python's `secrets` module for random number generation
- **Encrypted Storage**: Stores passwords encrypted using AES encryption (via Fernet)
- **Master Password Protection**: Database is protected by a master password with PBKDF2-HMAC key derivation
- **Unicode Support**: Utilizes 2,797 Unicode codepoints from multiple character sets including:
  - Latin alphabets (Basic, Extended-A, Extended-B)
  - Greek, Cyrillic, and IPA characters
  - Mathematical operators and symbols
  - Geometric shapes and box drawing characters
  - Currency symbols and number forms

## Installation

### Requirements

- Python 3.6 or higher
- cryptography library

### Setup

1. Clone the repository:
```bash
git clone https://github.com/alott2223/passwordmanager.git
cd passwordmanager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Run the interactive password manager:

```bash
python3 password_manager.py
```

You'll be prompted for a master password. The first time you run it, a new encrypted database will be created.

**Available Options:**
1. Generate and store new password
2. Retrieve password
3. List all services
4. Delete password
5. Exit

### Password Generator (Standalone)

Generate passwords directly:

```bash
python3 password_generator.py
```

Output example:
```
Unicode Codepoint Password Generator
==================================================
Character set size: 2,797 codepoints
Entropy per character: 11.45 bits
Minimum length for 86 bits: 8 characters
==================================================

Generated password: ▂İǞḄ⍦Ă≪ḷ
Password length: 8 characters
Actual entropy: 91.60 bits
```

### Python API

#### Generate a Password

```python
from password_generator import generate_password

# Generate with default settings (86+ bits entropy)
password, entropy = generate_password()
print(f"Password: {password}")
print(f"Entropy: {entropy:.2f} bits")

# Generate with custom length
password, entropy = generate_password(length=12)
print(f"Password: {password}")
print(f"Entropy: {entropy:.2f} bits")
```

#### Use the Password Manager

```python
from password_manager import PasswordManager

# Initialize the password manager
pm = PasswordManager()

# Unlock with master password
pm.unlock("my_master_password")

# Generate and store a new password
password = pm.add_password("github.com", "user@example.com")
print(f"Generated password: {password}")

# Store a custom password
pm.add_password("gmail.com", "user@gmail.com", "custom_password_123")

# Retrieve a password
entry = pm.get_password("github.com")
print(f"Username: {entry['username']}")
print(f"Password: {entry['password']}")

# List all services
services = pm.list_services()
print(f"Stored services: {services}")

# Delete a password
pm.delete_password("github.com")
```

## Security Features

### Entropy Analysis

- **Character set size**: 2,797 Unicode codepoints
- **Entropy per character**: 11.45 bits
- **Default password length**: 8 characters
- **Default entropy**: 91.60 bits (exceeds the 86-bit requirement)

This means there are approximately 2^91.6 ≈ 3.5 × 10^27 possible passwords, making brute-force attacks computationally infeasible.

### Encryption

- **Algorithm**: AES-128 (via Fernet symmetric encryption)
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Random Salt**: 16-byte cryptographic salt per database
- **Authenticated Encryption**: Fernet provides built-in authentication

### Best Practices

1. **Choose a strong master password**: Your master password should be long and unique
2. **Keep backups**: The encrypted database is stored at `~/.password_manager.enc` by default
3. **Don't share your master password**: Anyone with the master password can decrypt all stored passwords
4. **Verify entropy**: Each generated password displays its entropy for verification

## Testing

Run the test suite:

```bash
python3 test_password_manager.py
```

The test suite includes:
- Password generation tests
- Entropy calculation verification
- Encryption/decryption tests
- Database persistence tests
- Unicode encoding/decoding tests

## Technical Details

### Character Set Selection

The password generator uses carefully selected Unicode ranges to ensure:
- **Printability**: All characters are printable
- **Compatibility**: Characters encode/decode properly in UTF-8
- **Diversity**: Wide variety of character types for visual distinction
- **Usability**: Excludes problematic characters that might cause issues in various systems

### Cryptographic Randomness

The password generator uses Python's `secrets` module, which is designed for cryptographic purposes and uses the operating system's cryptographically secure random number generator.

### File Format

The encrypted database file structure:
```
[16 bytes: Salt][Variable: Fernet-encrypted JSON data]
```

The JSON data contains a dictionary mapping service names to credential objects:
```json
{
  "service_name": {
    "username": "user@example.com",
    "password": "generated_password"
  }
}
```

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Disclaimer

This is a demonstration password manager for educational purposes. For production use, consider established password managers with additional features like cloud sync, browser integration, and professional security audits.
