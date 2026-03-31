import subprocess
import os

def encrypt_data(data, passphrase):
    """Encrypts data using GPG AES-256."""
    try:
        process = subprocess.Popen(
            ['gpg', '--symmetric', '--cipher-algo', 'AES256', '--batch', '--passphrase-fd', '0', '--yes'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        
        # We need to send passphrase followed by newline and then the data if using passphrase-fd 0
        # Wait, passphrase-fd 0 is stdin. But we also need to send data through stdin.
        # Better to use --passphrase-fd 3 and pass passphrase there.
        
        pass_read, pass_write = os.pipe()
        os.write(pass_write, passphrase.encode() + b'\n')
        os.close(pass_write)
        
        process = subprocess.Popen(
            ['gpg', '--symmetric', '--cipher-algo', 'AES256', '--batch', '--passphrase-fd', str(pass_read), '--yes'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            pass_fds=(pass_read,),
            text=False
        )
        
        stdout, stderr = process.communicate(input=data.encode('utf-8'))
        os.close(pass_read)
        
        if process.returncode != 0:
            raise Exception(f"GPG encryption failed: {stderr.decode()}")
            
        return stdout
    except Exception as e:
        raise Exception(f"Encryption error: {str(e)}")

def decrypt_data(encrypted_data, passphrase):
    """Decrypts data using GPG."""
    try:
        pass_read, pass_write = os.pipe()
        os.write(pass_write, passphrase.encode() + b'\n')
        os.close(pass_write)
        
        process = subprocess.Popen(
            ['gpg', '--decrypt', '--batch', '--passphrase-fd', str(pass_read), '--yes'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            pass_fds=(pass_read,),
            text=False
        )
        
        stdout, stderr = process.communicate(input=encrypted_data)
        os.close(pass_read)
        
        if process.returncode != 0:
            raise Exception(f"GPG decryption failed: {stderr.decode()}")
            
        return stdout.decode('utf-8')
    except Exception as e:
        raise Exception(f"Decryption error: {str(e)}")
