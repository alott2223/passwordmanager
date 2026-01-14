#!/usr/bin/env python3
"""
Password Manager with Unicode Codepoint-based Password Generation

This is a simple password manager that:
1. Generates secure passwords using Unicode codepoints (86+ bits of entropy)
2. Stores passwords encrypted locally
3. Allows retrieval of stored passwords
"""

import os
import json
import getpass
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from password_generator import generate_password, get_charset_info


class PasswordManager:
    """A simple encrypted password manager."""
    
    def __init__(self, storage_file=None):
        """
        Initialize the password manager.
        
        Args:
            storage_file: Path to the encrypted storage file
        """
        if storage_file is None:
            storage_file = os.path.expanduser('~/.password_manager.enc')
        
        self.storage_file = storage_file
        self.master_password = None
        self.cipher = None
        self.passwords = {}
    
    def _derive_key(self, password, salt):
        """Derive an encryption key from the master password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def unlock(self, master_password):
        """
        Unlock the password manager with the master password.
        
        Args:
            master_password: The master password
        
        Returns:
            True if successful, False otherwise
        """
        self.master_password = master_password
        
        if os.path.exists(self.storage_file) and os.path.getsize(self.storage_file) > 0:
            # Load existing storage
            try:
                with open(self.storage_file, 'rb') as f:
                    data = f.read()
                
                # Extract salt (first 16 bytes)
                salt = data[:16]
                encrypted_data = data[16:]
                
                # Derive key and create cipher
                key = self._derive_key(master_password, salt)
                self.cipher = Fernet(key)
                
                # Decrypt and load passwords
                decrypted = self.cipher.decrypt(encrypted_data)
                self.passwords = json.loads(decrypted.decode())
                return True
            except Exception as e:
                print(f"Error unlocking: {e}")
                return False
        else:
            # Create new storage with random salt
            import secrets
            salt = secrets.token_bytes(16)
            key = self._derive_key(master_password, salt)
            self.cipher = Fernet(key)
            self.passwords = {}
            self._save(salt)
            return True
    
    def _save(self, salt=None):
        """Save the password database to disk."""
        if self.cipher is None:
            raise Exception("Password manager is locked")
        
        # If salt is not provided, read it from existing file
        if salt is None:
            with open(self.storage_file, 'rb') as f:
                salt = f.read(16)
        
        # Encrypt the password database
        data = json.dumps(self.passwords).encode()
        encrypted = self.cipher.encrypt(data)
        
        # Write salt + encrypted data
        with open(self.storage_file, 'wb') as f:
            f.write(salt + encrypted)
    
    def add_password(self, service, username=None, password=None, length=None):
        """
        Add a new password entry.
        
        Args:
            service: Name of the service/website
            username: Username/email (optional)
            password: Password (if None, generates a new one)
            length: Length for generated password (if None, uses minimum for 86 bits)
        
        Returns:
            The password (generated or provided)
        """
        if self.cipher is None:
            raise Exception("Password manager is locked")
        
        if password is None:
            password, entropy = generate_password(length=length)
            print(f"Generated password with {entropy:.2f} bits of entropy")
        
        entry = {
            'username': username,
            'password': password,
        }
        
        self.passwords[service] = entry
        self._save()
        
        return password
    
    def get_password(self, service):
        """
        Retrieve a password entry.
        
        Args:
            service: Name of the service/website
        
        Returns:
            Dictionary with username and password, or None if not found
        """
        if self.cipher is None:
            raise Exception("Password manager is locked")
        
        return self.passwords.get(service)
    
    def list_services(self):
        """
        List all stored services.
        
        Returns:
            List of service names
        """
        if self.cipher is None:
            raise Exception("Password manager is locked")
        
        return sorted(self.passwords.keys())
    
    def delete_password(self, service):
        """
        Delete a password entry.
        
        Args:
            service: Name of the service/website
        
        Returns:
            True if deleted, False if not found
        """
        if self.cipher is None:
            raise Exception("Password manager is locked")
        
        if service in self.passwords:
            del self.passwords[service]
            self._save()
            return True
        return False


def main():
    """Main CLI interface."""
    import sys
    
    # Show charset info
    info = get_charset_info()
    print("\n" + "=" * 60)
    print("Unicode Codepoint-based Password Manager")
    print("=" * 60)
    print(f"Character set size: {info['charset_size']:,} Unicode codepoints")
    print(f"Entropy per character: {info['entropy_per_char']:.2f} bits")
    print(f"Default password length: {info['min_length_for_86_bits']} chars (86+ bits entropy)")
    print("=" * 60 + "\n")
    
    # Initialize password manager
    pm = PasswordManager()
    
    # Get master password
    master_password = getpass.getpass("Enter master password: ")
    
    if not pm.unlock(master_password):
        print("Failed to unlock password manager!")
        sys.exit(1)
    
    print("Password manager unlocked successfully!\n")
    
    # Main menu loop
    while True:
        print("\nOptions:")
        print("  1. Generate and store new password")
        print("  2. Retrieve password")
        print("  3. List all services")
        print("  4. Delete password")
        print("  5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            service = input("Service name: ").strip()
            username = input("Username (optional): ").strip() or None
            
            custom = input("Generate password automatically? (Y/n): ").strip().lower()
            if custom == 'n':
                password = getpass.getpass("Enter password: ")
                pm.add_password(service, username, password)
            else:
                password = pm.add_password(service, username)
                print(f"\nGenerated password: {password}")
                print("(Copy this password now - it won't be shown again)")
            
            print(f"\n✓ Password saved for '{service}'")
        
        elif choice == '2':
            service = input("Service name: ").strip()
            entry = pm.get_password(service)
            
            if entry:
                print(f"\nService: {service}")
                if entry['username']:
                    print(f"Username: {entry['username']}")
                print(f"Password: {entry['password']}")
            else:
                print(f"\n✗ No password found for '{service}'")
        
        elif choice == '3':
            services = pm.list_services()
            
            if services:
                print(f"\nStored passwords ({len(services)}):")
                for service in services:
                    entry = pm.get_password(service)
                    username = entry['username'] or "(no username)"
                    print(f"  - {service}: {username}")
            else:
                print("\nNo passwords stored yet.")
        
        elif choice == '4':
            service = input("Service name: ").strip()
            
            if pm.delete_password(service):
                print(f"\n✓ Password deleted for '{service}'")
            else:
                print(f"\n✗ No password found for '{service}'")
        
        elif choice == '5':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid option. Please try again.")


if __name__ == '__main__':
    main()
