import json
import random
import smtplib
import re
from datetime import datetime
from email.mime.text import MIMEText

class Account:
    def __init__(self, account_number, pin, name, mobile, email, balance=0):
        self.account_number = account_number
        self.pin = pin
        self.name = name
        self.mobile = mobile
        self.email = email
        self.balance = balance
        self.transaction_history = []

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'type': 'deposit',
            'amount': amount
        })

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.transaction_history.append({
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'type': 'withdrawal',
                'amount': amount
            })
            return True
        return False

    def transfer(self, recipient, amount):
        if self.balance >= amount:
            self.withdraw(amount)
            recipient.deposit(amount)
            return True
        return False
    
    def calculate_interest(self, rate=4.0):
        interest = (self.balance * rate) / 100
        self.deposit(interest)
        return interest
    
    def get_balance(self):
        return self.balance

    def get_transaction_history(self):
        return self.transaction_history

class BankApp:
    def __init__(self):
        self.accounts = self.load_accounts()
        self.current_account = None

    def load_accounts(self):
        try:
            with open('accounts.json', 'r') as f:
                data = json.load(f)
                return {int(k): Account(**v) for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_accounts(self):
        with open('accounts.json', 'w') as f:
            data = {k: v.__dict__ for k, v in self.accounts.items()}
            json.dump(data, f, indent=4)

    def send_email(self, recipient, subject, body):
        sender_email = "yourbank@example.com"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient
        
        try:
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login("yourbank@example.com", "password")
                server.sendmail(sender_email, recipient, msg.as_string())
        except Exception as e:
            print("Email sending failed:", e)

    def create_account(self, name, pin, mobile, email):
        if not re.match(r'^[6-9]\d{9}$', mobile):
            print("Invalid mobile number. Must be 10 digits.")
            return None
        
        account_number = random.randint(10**9, 10**10-1)
        while account_number in self.accounts:
            account_number = random.randint(10**9, 10**10-1)
        
        new_account = Account(account_number, pin, name, mobile, email)
        self.accounts[account_number] = new_account
        self.save_accounts()
        self.send_email(email, "Account Created", f"Your account number is {account_number}.")
        return account_number

    def login(self, account_number, pin):
        account = self.accounts.get(account_number)
        if account and account.pin == pin:
            self.current_account = account
            return True
        return False

    def main_menu(self):
        while True:
            print("\nWelcome to SimpleBank")
            print("1. Create Account")
            print("2. Login")
            print("3. Exit")
            choice = input("Enter choice: ")

            if choice == '1':
                name = input("Enter your name: ")
                pin = input("Create a 4-digit PIN: ")
                mobile = input("Enter your mobile number: ")
                email = input("Enter your email: ")
                if len(pin) == 4 and pin.isdigit():
                    acc_num = self.create_account(name, pin, mobile, email)
                    if acc_num:
                        print(f"Account created! Your account number is: {acc_num}")
                else:
                    print("Invalid PIN. Must be 4 digits.")

            elif choice == '2':
                acc_num = int(input("Enter account number: "))
                pin = input("Enter PIN: ")
                if self.login(acc_num, pin):
                    self.account_menu()
                else:
                    print("Invalid credentials")

            elif choice == '3':
                self.save_accounts()
                print("Thank you for banking with us!")
                break

            else:
                print("Invalid choice")

    def account_menu(self):
        while self.current_account:
            print("\nAccount Menu")
            print("1. Check Balance")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Transfer")
            print("5. Transaction History")
            print("6. Calculate Interest")
            print("7. Logout")
            choice = input("Enter choice: ")

            if choice == '1':
                print(f"Your balance: ₹{self.current_account.get_balance():,.2f}")
            elif choice == '2':
                amount = float(input("Enter deposit amount: ₹"))
                self.current_account.deposit(amount)
                self.save_accounts()
                print("Deposit successful")
            elif choice == '3':
                amount = float(input("Enter withdrawal amount: ₹"))
                if self.current_account.withdraw(amount):
                    self.save_accounts()
                    print("Withdrawal successful")
                else:
                    print("Insufficient funds")
            elif choice == '4':
                recipient_acc = int(input("Enter recipient account number: "))
                amount = float(input("Enter transfer amount: ₹"))
                recipient = self.accounts.get(recipient_acc)
                if recipient and self.current_account.transfer(recipient, amount):
                    self.save_accounts()
                    print("Transfer successful")
                else:
                    print("Transfer failed")
            elif choice == '5':
                print("\nTransaction History:")
                for transaction in self.current_account.get_transaction_history():
                    print(f"{transaction['date']} - {transaction['type'].title()}: ₹{transaction['amount']:,.2f}")
            elif choice == '6':
                interest = self.current_account.calculate_interest()
                self.save_accounts()
                print(f"Interest added: ₹{interest:,.2f}")
            elif choice == '7':
                self.current_account = None
                print("Logged out successfully")
                break
            else:
                print("Invalid choice")

if __name__ == "__main__":
    app = BankApp()
    app.main_menu()
