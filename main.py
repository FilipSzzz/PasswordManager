from cryptography.fernet import Fernet
from tabulate import tabulate
import base64
import os
import time
import json

class PasswordManager:
    USERS = 'users.json'


    def __init__(self):
        self.current_user = None
        self.current_path = None
        self.key = None
        self.cipher = None
        self.encrypted_password = None #password to login
        self.decrypted_password = None
        self.cipher_user = None
        self.encrypted_password_user = None #passwords inside
        self.decrypted_password_user = None
    def menu(self):
        while True:
            print("1. Login")
            print("2. Create new account")
            print("3. Delete account")
            print("4. Exit")
            choice = input("What would you like to do? ")

            if choice == '1':
                return self.login()
            elif choice == '2':
                return self.new_user()
            elif choice == '3':
                return self.delete_user()
            elif choice == '4':
                print("Thank you for using the Password Manager. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def new_user(self):
        new_login = input("Login: ")
        new_password = input("Password: ")
        path = input("Select path to save passwords (example: C:\\Users\\MyUser\\Documents): ")
        name_of_file = input("What is the name of the file: ")

        #GENERATING KEY
        key = Fernet.generate_key()
        cipher = Fernet(key)

        #ENCRYPT PASSWORD
        encrypted_password = cipher.encrypt(new_password.encode())

        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except PermissionError:
                print(f"Error: Permission denied. Unable to create directory {path}")
                return False
            except Exception as e:
                print(f"An error occurred while creating directory: {e}")
                return False

        file_path = os.path.join(path, f"{name_of_file}.txt")
        content = f"User: {new_login}\nSaved passwords:\n"

        try:
            with open(file_path, "w") as file:
                file.write(content)
            print(f"File '{name_of_file}' has been created in {path}")
            self.current_path = file_path
        except PermissionError:
            print(f"Error: Permission denied. Unable to create file in {path}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

        users = {}
        # Changing into str
        key_str = base64.b64encode (key).decode ()
        encrypted_password_str = base64.b64encode (encrypted_password).decode ()
        if os.path.exists(self.USERS):
            try:
                with open(self.USERS, 'r') as f:
                    users = json.load(f)
            except json.JSONDecodeError:
                users = {}

        users[new_login] = {'key': key_str, 'password': encrypted_password_str, 'file_path': file_path}

        try:
            with open(self.USERS, 'w') as f:
                json.dump(users, f, indent=4)
        except Exception as e:
            print(f"Error saving user data: {e}")
            return False

    def login(self):
        if not os.path.exists(self.USERS):
            print("No accounts exist. Please create a new account.")
            return False

        try:
            with open(self.USERS, 'r') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = {}

        login = input("Login: ")
        password = input("Password: ")

        if login in users:

            key = base64.b64decode(users[login]['key'])
            encrypted_password = base64.b64decode(users[login]['password'])
            cipher = Fernet(key)

            decrypted_password = cipher.decrypt(encrypted_password).decode()

            if password == decrypted_password:
                print("Login successful!")
                self.current_user = login
                self.current_path = users[login]['file_path']
                self.key = key
                self.cipher = cipher
                self.encrypted_password = encrypted_password
                self.decrypted_password = decrypted_password
                time.sleep(1)
                print("_________________________________")
                self.after_login()
                return True

    def after_login(self):
        while True:
            print("1. Add new password")
            print("2. Display all passwords")
            print("3. Delete password")
            print("4. Change password")
            print("5. Exit")
            choice = input("What would you like to do? ")

            if choice == '1':
                self.add_password()
                print ("_________________________________")
            elif choice == '2':
                self.display_password()
                print ("_________________________________")
            elif choice == '3':
                self.delete_password()
                print ("_________________________________")
            elif choice == '4':
                self.change_password()
                print ("_________________________________")
            elif choice == '5':
                print("Thank you for using the Password Manager. Goodbye!")
                exit()

    def delete_user(self):
        with open(self.USERS, 'r') as f:
            users = json.load(f)

        ask = input("Are you sure you want to delete this account? (y/n) ").lower()

        if ask == 'y':
            login = input("Login: ")
            password = input("Password: ")

            if login in users and users[login]['password'] == password:
                try:
                    # Usuwanie pliku z hasłami
                    file_path = users[login]['file_path']
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"Password file '{file_path}' deleted successfully.")
                    else:
                        print("Password file not found.")

                    # Usuwanie użytkownika z bazy
                    del users[login]

                    with open(self.USERS, 'w') as f:
                        json.dump(users, f, indent=4)

                    print("Account and password file deleted successfully!")

                except Exception as e:
                    print(f"Error during deletion: {str(e)}")
                    return False

            else:
                print("Invalid login or password.")

        else:
            print("Account deletion cancelled.")

    def add_password(self):
        if not self.current_path:
            print ("No current path. Please select a path first.")
            return False

        login = input ("Enter login: ").strip ()
        password = input ("Enter password: ").strip ()

        # Generate a unique key for this password
        key = self.generate_key ()
        cipher = Fernet (key)

        # Encrypt the password
        encrypted_password = cipher.encrypt (password.encode ())

        try:
            with open (self.current_path, 'a') as f:
                # Store the key and encrypted password
                f.write (
                    f"\n{login}: {base64.b64encode (key).decode ()}:{base64.b64encode (encrypted_password).decode ()}")
            print ("Password added successfully!")
            print ("_________________________________")
        except Exception as e:
            print (f"Error adding password: {str (e)}")

    def display_password(self):
        try:
            with open (self.current_path, 'r') as f:
                lines = f.readlines ()

            table_data = []
            for line in lines[2:]:  # Skip the first two lines
                if ':' in line:
                    login, key_b64, encrypted_password_b64 = line.strip ().split (':', 2)
                    key = base64.b64decode (key_b64)
                    encrypted_password = base64.b64decode (encrypted_password_b64)

                    cipher = Fernet (key)
                    decrypted_password = cipher.decrypt (encrypted_password).decode ()

                    table_data.append ([login.strip (), decrypted_password])

            if table_data:
                print ("\nSaved passwords:")
                print (tabulate (table_data, headers=['Login', 'Password'], tablefmt="fancy_grid"))
            else:
                print ("No passwords saved.")
        except FileNotFoundError:
            print ("Password file not found!")
        except Exception as e:
            print (f"Error displaying passwords: {str (e)}")


    def delete_password(self):
        ask = input("Enter login for password deletion: ")
        try:
            with open(self.current_path, 'r') as f:
                lines = f.readlines()

            updated_lines = []
            deleted = False
            for line in lines:
                if line.strip() != "" and ":" in line:
                    login, password = line.split(":", 1)
                    if login.strip() != ask:
                        updated_lines.append(line)
                    else:
                        deleted = True
                else:
                    updated_lines.append(line)

            with open(self.current_path, 'w') as f:
                f.writelines(updated_lines)

            if deleted:
                print("Password deleted successfully!")
            else:
                print("Login not found in password file.")

        except FileNotFoundError:
            print("Password file not found!")
        except Exception as e:
            print(f"Error deleting password: {e}")

    def change_password(self):
        ask = input("Enter login for password change: ")
        new_password = input("Enter the new password: ")

        try:
            with open(self.current_path, 'r') as f:
                lines = f.readlines()

            updated_lines = []
            found = False
            for line in lines:
                if line.strip() != "" and ":" in line:
                    login, password = line.split(":", 1)
                    if login.strip() == ask:
                        updated_lines.append(f"{login}: {new_password}\n")
                        found = True
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            if not found:
                print("Login not found in password file.")
                return False

            with open(self.current_path, 'w') as f:
                f.writelines(updated_lines)

            print("Password updated successfully!")

        except FileNotFoundError:
            print("Password file not found!")
        except Exception as e:
            print(f"Error changing password: {e}")

    def generate_key(self):
        return Fernet.generate_key ()

if __name__ == "__main__":
    password_manager = PasswordManager()
    password_manager.menu()
