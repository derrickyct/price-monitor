import win32cred


def get_password(target_name):
    try:
        creds = win32cred.CredRead(target_name, win32cred.CRED_TYPE_GENERIC, 0)
        password = creds['CredentialBlob']
        decoded_password = password.decode('utf-16-le')
        return decoded_password
    except Exception as e:
        print(f"Error retrieving credentials: {e}")
        return None
