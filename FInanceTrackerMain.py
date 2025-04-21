import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

class Account:
    def __init__(self, name, balance=0.0):
        self.name = name
        self.balance = balance
        self.transactions = TransactionQueue()

    def deposit(self, amount, description="Deposit"):
        self.balance += amount
        self.transactions.enqueue({
            "type": "Deposit",
            "amount": amount,
            "description": description
        })

    def withdraw(self, amount, description="Withdrawal"):
        if amount > self.balance:
            messagebox.showwarning("Insufficient Funds",
                                   f"Withdrawing {amount} exceeds balance {self.balance}")
        self.balance -= amount
        self.transactions.enqueue({
            "type": "Withdrawal",
            "amount": amount,
            "description": description
        })

class AccountNode:
    def __init__(self, account):
        self.account = account
        self.left = None
        self.right = None

class AccountBST:
    def __init__(self):
        self.root = None

    def insert(self, account):
        if self.root is None:
            self.root = AccountNode(account)
            return True
        return self.insert_recursive(self.root, account)

    def insert_recursive(self, node, account):
        if account.name == node.account.name: #Duplicate account name check
            return False
        elif account.name < node.account.name:
            if node.left is None:
                node.left = AccountNode(account)
                return True
            else:
                return self.insert_recursive(node.left, account)
        else:
            if node.right is None:
                node.right = AccountNode(account)
                return True
            else:
                return self.insert_recursive(node.right, account)

    def find(self, name): #Using a BST, search for an account by name.
        return self.find_recursive(self.root, name)

    def find_recursive(self, node, name):
        if node is None:
            return None
        if name == node.account.name:
            return node.account
        elif name < node.account.name:
            return self.find_recursive(node.left, name)
        else:
            return self.find_recursive(node.right, name)

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if not node:
            return
        self._inorder(node.left, result)
        result.append(node.account)
        self._inorder(node.right, result)

class TransactionNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class TransactionQueue:
    def __init__(self): #Pointers to front and back of queue
        self.front = None
        self.rear = None
        self.size = 0 #Size at the beginning

    def enqueue(self, item):
        node = TransactionNode(item)
        if self.rear is None: #When queue is empty
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def dequeue(self):
        if self.front is None:
            return None
        item = self.front.data
        self.front = self.front.next
        if self.front is None: #Queue becomes empty
            self.rear = None
        self.size -= 1
        return item

    def __iter__(self):
        current = self.front
        while current:
            yield current.data
            current = current.next

class FinanceTracker:
    def __init__(self):
        self.accounts_tree = AccountBST() #Using Binary Search Tree and is used in most things (add_account() - tree insert, search_account(), update_balance(), list_account(), sort_accounts_by_balance(), save_to_file(), load_from_file())
        self.account_map = {} #Using hash map used only for checking for account duplicates (add_account())

    def add_account(self, name, initial_balance=0.0):
        if name in self.account_map: #hash map duplicate check
            messagebox.showerror("Error", "Account already exists.")
            return None
        acc = Account(name, initial_balance)
        self.accounts_tree.insert(acc) #BST insert
        self.account_map[name] = acc #Map insert
        return acc

    def search_account(self, name):
        return self.accounts_tree.find(name) #Uses BST

    def update_balance(self, name, amount, description=""):
        acc = self.search_account(name)
        if not acc:
            messagebox.showerror("Error", f"Account '{name}' not found.") #Tkinter notification
            return False
        if amount >= 0:
            acc.deposit(amount, description or "Deposit")
        else:
            acc.withdraw(-amount, description or "Withdrawal")
        return True

    def list_accounts(self): #List accounts by name
        return [(acc.name, acc.balance) for acc in self.accounts_tree.inorder()]

    def sort_accounts_by_balance(self, descending=False):
        accounts = self.accounts_tree.inorder()
        accounts.sort(key=lambda a: a.balance, reverse=descending) #The reverse sorts by High to low if descending is true, otherwise low to high
        return [(acc.name, acc.balance) for acc in accounts]

    def save_to_file(self, filename):
        data = []
        for acc in self.accounts_tree.inorder():
            data.append({
                "name": acc.name,
                "balance": acc.balance,
                "transactions": list(acc.transactions)
            })
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4) #Dump as JSON
        messagebox.showinfo("Saved", f"Data saved to {filename}") #Write to the Tkinter GUI

    def load_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.accounts_tree = AccountBST()
        self.account_map = {}
        for item in data: #Reconstruct the data
            acc = self.add_account(item['name'], item['balance'])
            for a in item.get('transactions', []):
                acc.transactions.enqueue(a)
        messagebox.showinfo("Loaded", f"Data loaded from {filename}") #Write to the Tkinter GUI

class FinanceTrackerGUI:
    def __init__(self, root):
        self.tracker = FinanceTracker()
        self.root = root
        root.title("Personal Finance Tracker")
        root.geometry("800x600")

        self.build_widgets()
        self.refresh_account_list()

    def build_widgets(self):
        # Account Frame
        frm = tk.Frame(self.root)
        frm.pack(pady=10)

        tk.Label(frm, text="Account Name:").grid(row=0, column=0)
        self.name_var = tk.StringVar()
        tk.Entry(frm, textvariable=self.name_var).grid(row=0, column=1)

        tk.Label(frm, text="Initial Balance:").grid(row=1, column=0)
        self.balance_var = tk.DoubleVar()
        tk.Entry(frm, textvariable=self.balance_var).grid(row=1, column=1)

        tk.Button(frm, text="Add Account", command=self.add_account).grid(row=2, column=0, columnspan=2, pady=5)

        # Account List
        self.tree = ttk.Treeview(self.root, columns=("Balance"), show='tree headings')
        self.tree.heading("#0", text="Account")
        self.tree.heading("Balance", text="Balance")
        self.tree.column("#0", width=300, anchor="w", stretch=True)
        self.tree.column("Balance", width=500, anchor="w", stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind('<<TreeviewSelect>>', self.on_account_select)

        # Transaction Frame
        tfrm = tk.Frame(self.root)
        tfrm.pack(pady=10)

        tk.Label(tfrm, text="Amount (+/-):").grid(row=0, column=0)
        self.amount_var = tk.DoubleVar()
        tk.Entry(tfrm, textvariable=self.amount_var).grid(row=0, column=1)

        tk.Label(tfrm, text="Description:").grid(row=1, column=0)
        self.desc_var = tk.StringVar()
        tk.Entry(tfrm, textvariable=self.desc_var).grid(row=1, column=1)

        tk.Button(tfrm, text="Deposit/Withdraw", command=self.transact).grid(row=2, column=0, columnspan=2, pady=5)

        # Bottom Buttons
        btnfrm = tk.Frame(self.root)
        btnfrm.pack(pady=10)
        tk.Button(btnfrm, text="Sort by Name", command=lambda: self.refresh_account_list()).pack(side=tk.LEFT, padx=5)
        tk.Button(btnfrm, text="Sort by Balance Asc", command=lambda: self.refresh_account_list(by_balance=False)).pack(side=tk.LEFT, padx=5)
        tk.Button(btnfrm, text="Sort by Balance Desc", command=lambda: self.refresh_account_list(by_balance=True)).pack(side=tk.LEFT, padx=5)
        tk.Button(btnfrm, text="Save", command=self.save_data).pack(side=tk.LEFT, padx=5)
        tk.Button(btnfrm, text="Load", command=self.load_data).pack(side=tk.LEFT, padx=5)

        # Transactions Display
        self.trans_text = tk.Text(self.root, height=10)
        self.trans_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def add_account(self):
        name = self.name_var.get().strip()
        bal = self.balance_var.get()
        if name:
            self.tracker.add_account(name, bal)
            self.name_var.set("")
            self.balance_var.set(0.0)
            self.refresh_account_list()
        else:
            messagebox.showerror("Error", "Please enter an account name.")

    def refresh_account_list(self, by_balance=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if by_balance is None:
            accounts = self.tracker.list_accounts()
        else:
            accounts = self.tracker.sort_accounts_by_balance(descending=by_balance)
        for name, bal in accounts:
            self.tree.insert("", "end", iid=name, values=(f"{bal:.2f}"), text=name)

    def on_account_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        name = sel[0]
        acc = self.tracker.search_account(name)
        self.display_transactions(acc)

    def transact(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Please select an account.")
            return
        name = sel[0]
        amt = self.amount_var.get()
        desc = self.desc_var.get().strip()
        if self.tracker.update_balance(name, amt, desc):
            self.amount_var.set(0.0)
            self.desc_var.set("")
            self.refresh_account_list()
            acc = self.tracker.search_account(name)
            self.display_transactions(acc)

    def display_transactions(self, acc):
        self.trans_text.delete(1.0, tk.END)
        if not acc:
            return
        for tr in acc.transactions:
            line = f"{tr['type']}: ${tr['amount']:.2f} -- {tr['description']}\n"
            self.trans_text.insert(tk.END, line)

    def save_data(self):
        fname = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON files", "*.json")])
        if fname:
            self.tracker.save_to_file(fname)

    def load_data(self):
        fname = filedialog.askopenfilename(defaultextension=".json",
                                           filetypes=[("JSON files", "*.json")])
        if fname:
            self.tracker.load_from_file(fname)
            self.refresh_account_list()

if __name__ == '__main__':
    root = tk.Tk()
    app = FinanceTrackerGUI(root)
    root.mainloop()
