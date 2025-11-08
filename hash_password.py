# hash_password.py
import getpass
from werkzeug.security import generate_password_hash

def main():
    """A simple command-line tool to hash a password."""
    password = getpass.getpass("Enter password to hash: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if not password or not password_confirm:
        print("Password cannot be empty.")
        return

    if password != password_confirm:
        print("Passwords do not match.")
        return

    hashed_password = generate_password_hash(password)
    print("\nPassword hash (copy this into your settings.json):")
    print(hashed_password)

if __name__ == "__main__":
    main()

