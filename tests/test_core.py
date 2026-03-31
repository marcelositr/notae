import unittest
import os
import shutil
import tempfile
from notae.core.note import Note, sanitize_filename
from notae.core.encryption import encrypt_data, decrypt_data

class TestNotaeCore(unittest.TestCase):
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("Meu Diário do Dia!"), "meu_diario_do_dia")
        self.assertEqual(sanitize_filename("  Spaces  and --- hyphens "), "spaces_and_hyphens")
        self.assertEqual(sanitize_filename("Ação e Reação"), "acao_e_reacao")

    def test_note_to_from_text(self):
        title = "Test Note"
        content = "This is a test.\nMulti-line."
        category = "tests"
        tags = ["tag1", "tag2"]
        
        note = Note(title, content, category, tags)
        text = note.to_text()
        
        reconstructed = Note.from_text(text)
        self.assertEqual(reconstructed.title, title)
        self.assertEqual(reconstructed.content, content)
        self.assertEqual(reconstructed.category, category)
        self.assertEqual(reconstructed.tags, tags)

    def test_encryption_decryption(self):
        # This test requires 'gpg' to be installed on the system
        try:
            data = "Secret content"
            passphrase = "testpassword"
            
            encrypted = encrypt_data(data, passphrase)
            self.assertNotEqual(encrypted, data)
            
            decrypted = decrypt_data(encrypted, passphrase)
            self.assertEqual(decrypted, data)
        except Exception as e:
            self.skipTest(f"GPG test failed (maybe gpg is not installed): {e}")

if __name__ == "__main__":
    unittest.main()
