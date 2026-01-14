#!/usr/bin/env python3
"""
Unicode Codepoint-based Password Generator

This module generates secure passwords using Unicode codepoints to achieve
at least 86 bits of entropy.
"""

import secrets
import math

# Unicode ranges for password generation
# We use a curated set of printable, non-problematic Unicode codepoints
# to ensure compatibility and usability

# Basic Latin and Latin-1 Supplement (printable characters)
UNICODE_RANGES = [
    (0x0021, 0x007E),  # Basic Latin printable (94 chars)
    (0x00A1, 0x00FF),  # Latin-1 Supplement (95 chars)
    (0x0100, 0x017F),  # Latin Extended-A (128 chars)
    (0x0180, 0x024F),  # Latin Extended-B (208 chars)
    (0x0250, 0x02AF),  # IPA Extensions (96 chars)
    (0x02B0, 0x02FF),  # Spacing Modifier Letters (80 chars)
    (0x0370, 0x03FF),  # Greek and Coptic (144 chars)
    (0x0400, 0x04FF),  # Cyrillic (256 chars)
    (0x0500, 0x052F),  # Cyrillic Supplement (48 chars)
    (0x1E00, 0x1EFF),  # Latin Extended Additional (256 chars)
    (0x2000, 0x206F),  # General Punctuation (112 chars)
    (0x2070, 0x209F),  # Superscripts and Subscripts (48 chars)
    (0x20A0, 0x20CF),  # Currency Symbols (48 chars)
    (0x2100, 0x214F),  # Letterlike Symbols (80 chars)
    (0x2150, 0x218F),  # Number Forms (64 chars)
    (0x2190, 0x21FF),  # Arrows (112 chars)
    (0x2200, 0x22FF),  # Mathematical Operators (256 chars)
    (0x2300, 0x23FF),  # Miscellaneous Technical (256 chars)
    (0x2460, 0x24FF),  # Enclosed Alphanumerics (160 chars)
    (0x2500, 0x257F),  # Box Drawing (128 chars)
    (0x2580, 0x259F),  # Block Elements (32 chars)
    (0x25A0, 0x25FF),  # Geometric Shapes (96 chars)
]


def build_codepoint_list():
    """Build a list of all valid Unicode codepoints for password generation."""
    codepoints = []
    for start, end in UNICODE_RANGES:
        for cp in range(start, end + 1):
            try:
                # Verify the codepoint can be encoded/decoded
                char = chr(cp)
                char.encode('utf-8')
                codepoints.append(cp)
            except (ValueError, UnicodeEncodeError):
                # Skip invalid codepoints
                continue
    return codepoints


# Global codepoint list
CODEPOINTS = build_codepoint_list()
CHARSET_SIZE = len(CODEPOINTS)


def calculate_entropy(password_length, charset_size=None):
    """
    Calculate the entropy in bits for a password.
    
    Args:
        password_length: Number of characters in the password
        charset_size: Size of the character set (defaults to CHARSET_SIZE)
    
    Returns:
        Entropy in bits
    """
    if charset_size is None:
        charset_size = CHARSET_SIZE
    
    return password_length * math.log2(charset_size)


def calculate_min_length(target_entropy_bits, charset_size=None):
    """
    Calculate the minimum password length needed for target entropy.
    
    Args:
        target_entropy_bits: Target entropy in bits
        charset_size: Size of the character set (defaults to CHARSET_SIZE)
    
    Returns:
        Minimum password length (integer)
    """
    if charset_size is None:
        charset_size = CHARSET_SIZE
    
    min_length = math.ceil(target_entropy_bits / math.log2(charset_size))
    return min_length


def generate_password(length=None, target_entropy=86):
    """
    Generate a cryptographically secure password using Unicode codepoints.
    
    Args:
        length: Desired password length (if None, calculates based on target_entropy)
        target_entropy: Target entropy in bits (default: 86)
    
    Returns:
        A tuple of (password string, actual entropy in bits)
    """
    if length is None:
        length = calculate_min_length(target_entropy)
    
    # Generate password using cryptographically secure random selection
    password_chars = []
    for _ in range(length):
        # Use secrets.choice for cryptographic randomness
        codepoint = secrets.choice(CODEPOINTS)
        password_chars.append(chr(codepoint))
    
    password = ''.join(password_chars)
    actual_entropy = calculate_entropy(length)
    
    return password, actual_entropy


def get_charset_info():
    """
    Get information about the character set being used.
    
    Returns:
        Dictionary with charset information
    """
    return {
        'charset_size': CHARSET_SIZE,
        'entropy_per_char': math.log2(CHARSET_SIZE),
        'min_length_for_86_bits': calculate_min_length(86),
        'unicode_ranges_count': len(UNICODE_RANGES),
    }


if __name__ == '__main__':
    # Demo usage
    info = get_charset_info()
    print("Unicode Codepoint Password Generator")
    print("=" * 50)
    print(f"Character set size: {info['charset_size']:,} codepoints")
    print(f"Entropy per character: {info['entropy_per_char']:.2f} bits")
    print(f"Minimum length for 86 bits: {info['min_length_for_86_bits']} characters")
    print("=" * 50)
    print()
    
    # Generate a password with at least 86 bits of entropy
    password, entropy = generate_password()
    print(f"Generated password: {password}")
    print(f"Password length: {len(password)} characters")
    print(f"Actual entropy: {entropy:.2f} bits")
    print()
    
    # Generate a few more examples
    print("Additional examples:")
    for i in range(3):
        pwd, ent = generate_password()
        print(f"  {pwd} ({ent:.2f} bits)")
