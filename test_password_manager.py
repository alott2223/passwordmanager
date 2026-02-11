#!/usr/bin/env python3
"""
Tests for the Unicode Codepoint-based Password Manager
"""

import unittest
import os
import tempfile
import math
from password_generator import (
    generate_password, 
    calculate_entropy, 
    calculate_min_length,
    get_charset_info,
    CHARSET_SIZE
)
from password_manager import PasswordManager


class TestPasswordGenerator(unittest.TestCase):
    """Test cases for password generation."""
    
    def test_charset_size(self):
        """Test that we have a reasonable charset size."""
        info = get_charset_info()
        charset_size = info['charset_size']
        
        # Should have at least 1000 codepoints for good entropy
        self.assertGreater(charset_size, 1000)
        
        # Should have less than 10000 to be practical
        self.assertLess(charset_size, 10000)
    
    def test_entropy_calculation(self):
        """Test entropy calculation is correct."""
        # With charset size N, entropy per char should be log2(N)
        expected_entropy_per_char = math.log2(CHARSET_SIZE)
        
        # For 1 character
        entropy_1 = calculate_entropy(1)
        self.assertAlmostEqual(entropy_1, expected_entropy_per_char, places=2)
        
        # For 8 characters
        entropy_8 = calculate_entropy(8)
        self.assertAlmostEqual(entropy_8, 8 * expected_entropy_per_char, places=2)
    
    def test_min_length_calculation(self):
        """Test minimum length calculation for target entropy."""
        # For 86 bits of entropy
        min_len = calculate_min_length(86)
        
        # Verify that this length gives at least 86 bits
        actual_entropy = calculate_entropy(min_len)
        self.assertGreaterEqual(actual_entropy, 86)
        
        # Verify that one less character would be insufficient
        if min_len > 1:
            insufficient_entropy = calculate_entropy(min_len - 1)
            self.assertLess(insufficient_entropy, 86)
    
    def test_password_generation(self):
        """Test that passwords are generated correctly."""
        password, entropy = generate_password()
        
        # Should generate a non-empty password
        self.assertIsNotNone(password)
        self.assertGreater(len(password), 0)
        
        # Should meet the 86-bit entropy requirement
        self.assertGreaterEqual(entropy, 86)
        
        # Password length should match the minimum required
        min_len = calculate_min_length(86)
        self.assertEqual(len(password), min_len)
    
    def test_password_uniqueness(self):
        """Test that generated passwords are unique."""
        passwords = set()
        
        # Generate 100 passwords
        for _ in range(100):
            password, _ = generate_password()
            passwords.add(password)
        
        # All should be unique (probability of collision is astronomically low)
        self.assertEqual(len(passwords), 100)
    
    def test_custom_length(self):
        """Test generating passwords with custom length."""
        custom_length = 12
        password, entropy = generate_password(length=custom_length)
        
        # Should have the requested length
        self.assertEqual(len(password), custom_length)
        
        # Entropy should match the length
        expected_entropy = calculate_entropy(custom_length)
        self.assertAlmostEqual(entropy, expected_entropy, places=2)
    
    def test_entropy_requirement(self):
        """Test that default passwords meet 86-bit entropy requirement."""
        # Generate multiple passwords and verify all meet requirement
        for _ in range(10):
            password, entropy = generate_password()
            self.assertGreaterEqual(entropy, 86, 
                f"Password '{password}' has only {entropy:.2f} bits of entropy")
    
    def test_unicode_encoding(self):
        """Test that generated passwords can be properly encoded/decoded."""
        for _ in range(20):
            password, _ = generate_password()
            
            # Should be encodable to UTF-8
            try:
                encoded = password.encode('utf-8')
                decoded = encoded.decode('utf-8')
                self.assertEqual(password, decoded)
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                self.fail(f"Password encoding/decoding failed: {e}")


class TestPasswordManager(unittest.TestCase):
    """Test cases for password manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.storage_file = self.temp_file.name
        self.master_password = "test_master_password_123"
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        if os.path.exists(self.storage_file):
            os.unlink(self.storage_file)
    
    def test_initialization(self):
        """Test password manager initialization."""
        pm = PasswordManager(self.storage_file)
        self.assertIsNotNone(pm)
        self.assertEqual(pm.storage_file, self.storage_file)
    
    def test_unlock_new_database(self):
        """Test unlocking a new password database."""
        pm = PasswordManager(self.storage_file)
        result = pm.unlock(self.master_password)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.storage_file))
    
    def test_unlock_existing_database(self):
        """Test unlocking an existing password database."""
        # Create and save a database
        pm1 = PasswordManager(self.storage_file)
        pm1.unlock(self.master_password)
        pm1.add_password("test_service", "user@example.com", "test_password")
        
        # Unlock the same database
        pm2 = PasswordManager(self.storage_file)
        result = pm2.unlock(self.master_password)
        
        self.assertTrue(result)
        
        # Verify data persisted
        entry = pm2.get_password("test_service")
        self.assertIsNotNone(entry)
        self.assertEqual(entry['username'], "user@example.com")
        self.assertEqual(entry['password'], "test_password")
    
    def test_wrong_master_password(self):
        """Test that wrong master password fails to unlock."""
        # Create a database
        pm1 = PasswordManager(self.storage_file)
        pm1.unlock(self.master_password)
        pm1.add_password("test_service", "user@example.com", "test_password")
        
        # Try to unlock with wrong password
        pm2 = PasswordManager(self.storage_file)
        result = pm2.unlock("wrong_password")
        
        self.assertFalse(result)
    
    def test_add_and_retrieve_password(self):
        """Test adding and retrieving passwords."""
        pm = PasswordManager(self.storage_file)
        pm.unlock(self.master_password)
        
        # Add a password
        pm.add_password("gmail", "user@gmail.com", "my_password_123")
        
        # Retrieve it
        entry = pm.get_password("gmail")
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry['username'], "user@gmail.com")
        self.assertEqual(entry['password'], "my_password_123")
    
    def test_generate_password(self):
        """Test generating a password automatically."""
        pm = PasswordManager(self.storage_file)
        pm.unlock(self.master_password)
        
        # Add with auto-generated password
        password = pm.add_password("github", "user@github.com")
        
        # Should have generated a password
        self.assertIsNotNone(password)
        self.assertGreater(len(password), 0)
        
        # Retrieve and verify
        entry = pm.get_password("github")
        self.assertEqual(entry['password'], password)
    
    def test_list_services(self):
        """Test listing all services."""
        pm = PasswordManager(self.storage_file)
        pm.unlock(self.master_password)
        
        # Add multiple services
        pm.add_password("service1", "user1", "pass1")
        pm.add_password("service2", "user2", "pass2")
        pm.add_password("service3", "user3", "pass3")
        
        # List services
        services = pm.list_services()
        
        self.assertEqual(len(services), 3)
        self.assertIn("service1", services)
        self.assertIn("service2", services)
        self.assertIn("service3", services)
    
    def test_delete_password(self):
        """Test deleting a password."""
        pm = PasswordManager(self.storage_file)
        pm.unlock(self.master_password)
        
        # Add and then delete
        pm.add_password("temp_service", "user", "pass")
        result = pm.delete_password("temp_service")
        
        self.assertTrue(result)
        
        # Verify it's gone
        entry = pm.get_password("temp_service")
        self.assertIsNone(entry)
    
    def test_delete_nonexistent(self):
        """Test deleting a non-existent password."""
        pm = PasswordManager(self.storage_file)
        pm.unlock(self.master_password)
        
        result = pm.delete_password("nonexistent_service")
        
        self.assertFalse(result)
    
    def test_persistence(self):
        """Test that data persists across manager instances."""
        # Create and populate database
        pm1 = PasswordManager(self.storage_file)
        pm1.unlock(self.master_password)
        pm1.add_password("persistent1", "user1", "pass1")
        pm1.add_password("persistent2", "user2", "pass2")
        
        # Create new instance and verify data
        pm2 = PasswordManager(self.storage_file)
        pm2.unlock(self.master_password)
        
        services = pm2.list_services()
        self.assertEqual(len(services), 2)
        self.assertIn("persistent1", services)
        self.assertIn("persistent2", services)
        
        entry1 = pm2.get_password("persistent1")
        self.assertEqual(entry1['password'], "pass1")


def run_tests():
    """Run all tests."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
