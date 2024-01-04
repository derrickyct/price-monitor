from cryptography.fernet import Fernet


def generate_key():
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    return cipher_suite


def encrypt_password(password, cipher_suite):
    try:
        encrypted_password = cipher_suite.encrypt(password)
        return encrypted_password
    except Exception as e:
        print(f"Error encoding password:: {e}")
        return None


def decrypt_password(encrypted_password, cipher_suite):
    try:
        decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
        return decrypted_password
    except Exception as e:
        print(f"Error decoding password: {e}")
        return None
