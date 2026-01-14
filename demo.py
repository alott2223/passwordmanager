#!/usr/bin/env python3
"""
Demo script showing the password manager capabilities
"""

import os
import tempfile
from password_generator import generate_password, get_charset_info
from password_manager import PasswordManager


def demo():
    """Run a demonstration of the password manager."""
    print("=" * 70)
    print("Unicode Codepoint-based Password Manager Demo")
    print("=" * 70)
    print()
    
    # Show character set information
    info = get_charset_info()
    print("📊 Character Set Statistics:")
    print(f"   • Total codepoints: {info['charset_size']:,}")
    print(f"   • Entropy per character: {info['entropy_per_char']:.2f} bits")
    print(f"   • Unicode ranges used: {info['unicode_ranges_count']}")
    print(f"   • Minimum length for 86 bits: {info['min_length_for_86_bits']} characters")
    print()
    
    # Generate some example passwords
    print("🔐 Example Generated Passwords:")
    for i in range(5):
        password, entropy = generate_password()
        print(f"   {i+1}. {password:20} ({entropy:.2f} bits of entropy)")
    print()
    
    # Demonstrate the password manager
    print("💾 Password Manager Demo:")
    
    # Create temporary storage
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    storage_file = temp_file.name
    
    try:
        # Initialize and unlock
        pm = PasswordManager(storage_file)
        pm.unlock("demo_master_password")
        print("   ✓ Password manager initialized and unlocked")
        
        # Add some passwords
        print("\n   Adding passwords...")
        pw1 = pm.add_password("github.com", "demo_user@example.com")
        print(f"   ✓ Added GitHub password: {pw1}")
        
        pw2 = pm.add_password("aws.amazon.com", "admin@company.com")
        print(f"   ✓ Added AWS password: {pw2}")
        
        pm.add_password("example.com", "user123", "my_custom_password")
        print(f"   ✓ Added custom password for example.com")
        
        # List all services
        print("\n   📋 Stored services:")
        services = pm.list_services()
        for service in services:
            entry = pm.get_password(service)
            print(f"      • {service:20} ({entry['username'] or 'no username'})")
        
        # Retrieve a password
        print("\n   🔍 Retrieving password for github.com:")
        entry = pm.get_password("github.com")
        print(f"      Username: {entry['username']}")
        print(f"      Password: {entry['password']}")
        
        # Test persistence
        print("\n   💿 Testing persistence (reload from disk)...")
        pm2 = PasswordManager(storage_file)
        pm2.unlock("demo_master_password")
        services2 = pm2.list_services()
        print(f"   ✓ Reloaded {len(services2)} passwords from encrypted storage")
        
        print("\n✅ Demo completed successfully!")
        
    finally:
        # Clean up
        if os.path.exists(storage_file):
            os.unlink(storage_file)
    
    print()
    print("=" * 70)
    print("Key Features:")
    print("  • 86+ bits of entropy (91.60 bits with default settings)")
    print("  • Cryptographically secure random generation")
    print("  • AES-128 encrypted storage")
    print("  • Master password protection with PBKDF2-HMAC")
    print("  • 2,797 Unicode codepoints for maximum variety")
    print("=" * 70)


if __name__ == '__main__':
    demo()
