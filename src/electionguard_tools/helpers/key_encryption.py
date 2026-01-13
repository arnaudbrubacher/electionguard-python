import os
import sys
import base64
from typing import Optional

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    # This might be imported in contexts where cryptography is not available
    # but encryption/decryption is not strictly required immediately.
    # We'll fail at runtime if functions are called.
    AESGCM = None

def _check_cryptography_installed():
    if AESGCM is None:
        raise ImportError(
            "The 'cryptography' library is required for guardian key encryption. "
            "Please install it with: pip install cryptography"
        )

def get_encryption_key() -> bytes:
    """Get the master encryption key from environment variable."""
    key_b64 = os.environ.get('GUARDIAN_KEY_ENCRYPTION_KEY')
    
    if not key_b64:
        raise ValueError("GUARDIAN_KEY_ENCRYPTION_KEY environment variable not set")
    
    try:
        key = base64.b64decode(key_b64)
    except Exception as e:
        raise ValueError(f"Invalid encryption key format (must be base64): {e}")
    
    if len(key) != 32:
        raise ValueError(f"Encryption key must be 32 bytes (256 bits), got {len(key)} bytes")
    
    return key

def encrypt_guardian_key(plaintext_bytes: bytes, key: Optional[bytes] = None) -> bytes:
    """
    Encrypt guardian key data using AES-256-GCM.
    
    Args:
        plaintext_bytes: Data to encrypt
        key: 32-byte encryption key (if None, retrieved from env)
        
    Returns:
        Encrypted data (nonce + ciphertext + tag)
    """
    _check_cryptography_installed()
    
    if key is None:
        key = get_encryption_key()
        
    if len(key) != 32:
        raise ValueError("Encryption key must be 32 bytes for AES-256")
    
    # AES-GCM with 12-byte nonce (standard size)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    
    # Encrypt
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
    
    # Return nonce + ciphertext (tag is included in ciphertext by cryptography lib)
    return nonce + ciphertext

def decrypt_guardian_key(encrypted_data: bytes, key: Optional[bytes] = None) -> bytes:
    """
    Decrypt guardian key data using AES-256-GCM.
    
    Args:
        encrypted_data: Encrypted data (nonce + ciphertext + tag)
        key: 32-byte encryption key (if None, retrieved from env)
        
    Returns:
        Decrypted plaintext bytes
    """
    _check_cryptography_installed()

    if key is None:
        key = get_encryption_key()
        
    if len(key) != 32:
        raise ValueError("Decryption key must be 32 bytes for AES-256")
    
    # AES-GCM with 12-byte nonce (standard size)
    aesgcm = AESGCM(key)
    nonce_size = 12
    
    if len(encrypted_data) < nonce_size:
        raise ValueError(f"Ciphertext too short (minimum {nonce_size} bytes, got {len(encrypted_data)})")
    
    # Extract nonce from beginning of ciphertext
    nonce = encrypted_data[:nonce_size]
    ciphertext = encrypted_data[nonce_size:]
    
    # Decrypt and verify authentication tag
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(f"Decryption failed (wrong key or corrupted data): {e}")
    
    return plaintext
