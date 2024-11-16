import tkinter as tk
from tkinter import messagebox
import random
from datetime import datetime
import json

ACCOUNTFILE = "accounts.json"

def saveAccounts(accountsDb):
    with open(ACCOUNTFILE, "w") as file:
        json.dump({key: account.toDict() for key, account in accountsDb.items()}, file, indent=4)

def loadAccounts():
    try:
        with open(ACCOUNTFILE, "r") as file:
            data = json.load(file)
            return {key: Account.fromDict(value) for key, value in data.items()}
    except FileNotFoundError:
        return {}

class ATM:
    def __init__(self, atmId, availableBalance):
        self.atmId = atmId
        self.availableBalance = availableBalance

    def withdrawCash(self, account, amount):
        if amount > account.balance:
            return "Insufficient funds in your account."
        elif amount > self.availableBalance:
            return f"ATM doesn't have enough funds. Maximum withdrawable: {self.availableBalance} TL."
        else:
            account.balance -= amount
            self.availableBalance -= amount
            return f"Success! You have withdrawn {amount} TL. New balance: {account.balance} TL."


class Account:
    def __init__(self, accountNumber, pin, balance=1000000):
        self.accountNumber = accountNumber
        self.pin = pin
        self.balance = balance

    def toDict(self):
        return {
            "accountNumber": self.accountNumber,
            "pin": self.pin,
            "balance": self.balance
        }

    @classmethod
    def fromDict(cls, data):
        return cls(data['accountNumber'], data['pin'], data['balance'])


class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM System")
        self.atm = ATM("ATM-001", 5000)
        self.accountsDb = loadAccounts()
        self.account = None
        self.root.configure(bg="green") 
        self.createWidgets()

    def createWidgets(self):
        self.welcomeLabel = tk.Label(self.root, text="WELCOME TO InfoSuper Bank", font=("Arial", 24), fg="white", bg="green")
        self.welcomeLabel.pack(pady=50)

        self.accountFrame = tk.Frame(self.root, bg="green")
        self.accountFrame.pack(pady=20)
        
        self.accountLabel = tk.Label(self.accountFrame, text="Enter Account Number:", fg="white", bg="green")
        self.accountLabel.grid(row=0, column=0)
        self.accountEntry = tk.Entry(self.accountFrame)
        self.accountEntry.grid(row=0, column=1)

        self.pinLabel = tk.Label(self.accountFrame, text="Enter PIN:", fg="white", bg="green")
        self.pinLabel.grid(row=1, column=0)
        self.pinEntry = tk.Entry(self.accountFrame, show="*")
        self.pinEntry.grid(row=1, column=1)

        self.loginButton = tk.Button(self.accountFrame, text="Login", command=self.login)
        self.loginButton.grid(row=2, columnspan=2)

    def login(self):
        accountNumber = self.accountEntry.get()
        pin = self.pinEntry.get()
        if accountNumber in self.accountsDb:
            self.account = self.accountsDb[accountNumber]
            if self.account.pin == pin:
                messagebox.showinfo("Login Successful", "PIN verified successfully.")
                self.showWithdrawalScreen()
            else:
                messagebox.showerror("Login Failed", "Incorrect PIN. Please try again.")
        else:
            messagebox.showinfo("Account Not Found", "Account number not found. You can set a new PIN.")
            self.setPin(accountNumber)

    def setPin(self, accountNumber):
        newPin = self.pinEntry.get()
        newAccount = Account(accountNumber, newPin)
        self.accountsDb[accountNumber] = newAccount
        self.account = newAccount
        saveAccounts(self.accountsDb)
        messagebox.showinfo("Account Created", "Account created successfully with a new PIN.")
        self.showWithdrawalScreen()

    def showWithdrawalScreen(self):
        self.accountFrame.destroy()
        self.withdrawalFrame = tk.Frame(self.root, bg="green")
        self.withdrawalFrame.pack(pady=20)

        self.withdrawLabel = tk.Label(self.withdrawalFrame, text="Select amount to withdraw:", fg="white", bg="green")
        self.withdrawLabel.pack()

        self.amountButtons = [
            tk.Button(self.withdrawalFrame, text="50 TL", command=lambda: self.withdraw(50)),
            tk.Button(self.withdrawalFrame, text="100 TL", command=lambda: self.withdraw(100)),
            tk.Button(self.withdrawalFrame, text="200 TL", command=lambda: self.withdraw(200)),
            tk.Button(self.withdrawalFrame, text="1000 TL", command=lambda: self.withdraw(1000)),
            tk.Button(self.withdrawalFrame, text="Custom Amount", command=self.customAmount)
        ]

        for button in self.amountButtons:
            button.pack(fill='x', pady=5)  

    def withdraw(self, amount):
        result = self.atm.withdrawCash(self.account, amount)
        messagebox.showinfo("Transaction Result", result)

        if result.startswith("Success"):
            self.showReceipt(amount)
            saveAccounts(self.accountsDb) 

    def customAmount(self):
        self.customAmountWindow = tk.Toplevel(self.root)
        self.customAmountWindow.title("Enter Custom Amount")
        self.customAmountWindow.configure(bg="green")

        self.customAmountLabel = tk.Label(self.customAmountWindow, text="Enter the amount to withdraw:", fg="white", bg="green")
        self.customAmountLabel.pack()

        self.customAmountEntry = tk.Entry(self.customAmountWindow)
        self.customAmountEntry.pack()

        self.submitButton = tk.Button(self.customAmountWindow, text="Submit", command=self.processCustomAmount)
        self.submitButton.pack()

    def processCustomAmount(self):
        try:
            amount = int(self.customAmountEntry.get())
            if amount > 0:
                result = self.atm.withdrawCash(self.account, amount)
                messagebox.showinfo("Transaction Result", result)
                if result.startswith("Success"):
                    self.showReceipt(amount)
                    saveAccounts(self.accountsDb)
            else:
                messagebox.showerror("Invalid Amount", "Amount must be positive.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
        self.customAmountWindow.destroy()

    def showReceipt(self, amount):
        transactionId = random.randint(100000, 999999)
        transactionDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        remainingBalance = self.account.balance
        receipt = f"""
        Transaction ID: {transactionId}
        Date: {transactionDate}
        Account Number: {self.account.accountNumber}
        Amount Withdrawn: {amount} TL
        Remaining Balance: {remainingBalance} TL
        Thank you for choosing InfoSuper Bank!
        """
        messagebox.showinfo("Receipt", receipt)

        self.askNewTransaction()

    def askNewTransaction(self):
        nextAction = messagebox.askyesno("New Transaction", "Would you like to perform another transaction?")
        if nextAction:
            self.showWithdrawalScreen()
        else:
            self.root.quit()

root = tk.Tk()
atmApp = ATMApp(root)
root.mainloop()