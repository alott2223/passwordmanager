#!/usr/bin/env python3
"""
Simple command-line wrapper for the password manager.

Usage:
    ./pwm.py                    # Interactive mode
    ./pwm.py generate           # Generate a password without storing
    ./pwm.py info               # Show character set information
"""

import sys
from password_generator import generate_password, get_charset_info
from password_manager import main as run_manager


def show_info():
    """Display information about the password generator."""
    info = get_charset_info()
    print("\nUnicode Codepoint Password Generator Information")
    print("=" * 60)
    print(f"Character set size:      {info['charset_size']:,} codepoints")
    print(f"Entropy per character:   {info['entropy_per_char']:.2f} bits")
    print(f"Default password length: {info['min_length_for_86_bits']} characters")
    print(f"Default entropy:         {info['entropy_per_char'] * info['min_length_for_86_bits']:.2f} bits")
    print(f"Unicode ranges used:     {info['unicode_ranges_count']}")
    print("=" * 60)
    print("\nThis exceeds the 86-bit entropy requirement.")
    print()


def generate_only(count=1):
    """Generate password(s) without storing them."""
    print(f"\nGenerating {count} password(s):\n")
    
    for i in range(count):
        password, entropy = generate_password()
        print(f"{i+1}. {password}")
        print(f"   Entropy: {entropy:.2f} bits")
        print()


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'generate' or command == 'gen':
            try:
                count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
                if count < 1:
                    print("Error: Count must be a positive integer")
                    sys.exit(1)
                generate_only(count)
            except ValueError:
                print(f"Error: Invalid count value '{sys.argv[2]}'. Must be an integer.")
                sys.exit(1)
        elif command == 'info':
            show_info()
        elif command == 'help' or command == '--help' or command == '-h':
            print(__doc__)
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' for usage information.")
            sys.exit(1)
    else:
        # Run interactive mode
        run_manager()


if __name__ == '__main__':
    main()
