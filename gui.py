import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu
import database

class App:
    def __init__(self):
        database.init_db()
        self.root = tk.Tk()
        self.root.title("Система учета клиентов банка")
        self.root.geometry("400x300")

        self.label = tk.Label(self.root, text="Добро пожаловать в систему учета клиентов!")
        self.label.pack(pady=20)

        self.add_client_button = tk.Button(self.root, text="Добавить клиента", command=self.add_client)
        self.add_client_button.pack(pady=10)

        self.view_clients_button = tk.Button(self.root, text="Список клиентов", command=self.view_clients)
        self.view_clients_button.pack(pady=10)

        self.generate_contract_button = tk.Button(self.root, text="Сгенерировать договор", command=self.generate_contract)
        self.generate_contract_button.pack(pady=10)

        self.view_transactions_button = tk.Button(self.root, text="Список транзакций", command=self.view_transactions)
        self.view_transactions_button.pack(pady=10)

        self.view_debts_button = tk.Button(self.root, text="Список долгов", command=self.view_debts)
        self.view_debts_button.pack(pady=10)

    def add_client(self):
        self.open_add_client_window()

    def open_add_client_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить клиента")
        add_window.geometry("300x200")

        tk.Label(add_window, text="Имя клиента").pack(pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.pack(pady=5)

        tk.Label(add_window, text="Телефон клиента").pack(pady=5)
        phone_entry = tk.Entry(add_window)
        phone_entry.pack(pady=5)

        tk.Label(add_window, text="Email клиента").pack(pady=5)
        email_entry = tk.Entry(add_window)
        email_entry.pack(pady=5)

        def save_client():
            name = name_entry.get()
            phone = phone_entry.get()
            email = email_entry.get()

            if name:
                database.add_client(name, phone, email)
                messagebox.showinfo("Успех", "Клиент добавлен успешно!")
                add_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Имя клиента обязательно!")

        save_button = tk.Button(add_window, text="Сохранить", command=save_client)
        save_button.pack(pady=10)

    def view_clients(self):
        clients = database.get_all_clients()
        view_window = tk.Toplevel(self.root)
        view_window.title("Список клиентов")
        view_window.geometry("400x300")

        text = tk.Text(view_window)
        text.pack(expand=True, fill='both')

        text.insert(tk.END, "ID\tИмя\tТелефон\tEmail\n")
        text.insert(tk.END, "-" * 50 + "\n")

        for client in clients:
            text.insert(tk.END, f"{client[0]}\t{client[1]}\t{client[2]}\t{client[3]}\n")

        text.config(state=tk.DISABLED)

    def generate_contract(self):
        contract_window = tk.Toplevel(self.root)
        contract_window.title("Генерация договора")
        contract_window.geometry("400x300")

        tk.Label(contract_window, text="ID клиента").pack(pady=5)
        client_id_entry = tk.Entry(contract_window)
        client_id_entry.pack(pady=5)

        tk.Label(contract_window, text="Номер договора").pack(pady=5)
        contract_number_entry = tk.Entry(contract_window)
        contract_number_entry.pack(pady=5)

        tk.Label(contract_window, text="Тип договора").pack(pady=5)

        contract_type_var = StringVar(contract_window)
        contract_type_var.set("Договор на оказание услуг")  # значение по умолчанию
        contract_types = ["Договор на оказание услуг", "Договор на прекращение оказания услуг", "Договор на займ"]
        
        contract_type_menu = OptionMenu(contract_window, contract_type_var, *contract_types)
        contract_type_menu.pack(pady=5)

        tk.Label(contract_window, text="Сумма займа (если применимо)").pack(pady=5)
        loan_amount_entry = tk.Entry(contract_window)
        loan_amount_entry.pack(pady=5)

        def create_contract():
            client_id = client_id_entry.get()
            contract_number = contract_number_entry.get()
            contract_type = contract_type_var.get()

            loan_amount = loan_amount_entry.get()
            if loan_amount:
                loan_amount = float(loan_amount)
            else:
                loan_amount = 0

            if client_id and contract_number:
                try:
                    if contract_type == "Договор на займ":
                        database.add_transaction(int(client_id), loan_amount, "долг")
                    file_name = database.generate_contract(int(client_id), contract_number, contract_type)
                    messagebox.showinfo("Успех", f"Договор создан: {file_name}")
                    contract_window.destroy()
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
            else:
                messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля.")

        generate_button = tk.Button(contract_window, text="Создать договор", command=create_contract)
        generate_button.pack(pady=10)

    def view_transactions(self):
        transactions = database.get_all_transactions()
        view_window = tk.Toplevel(self.root)
        view_window.title("Список транзакций")
        view_window.geometry("400x300")

        text = tk.Text(view_window)
        text.pack(expand=True, fill='both')

        text.insert(tk.END, "ID\tКлиент ID\tСумма\tТип\tДата\n")
        text.insert(tk.END, "-" * 50 + "\n")

        for transaction in transactions:
            text.insert(tk.END, f"{transaction[0]}\t{transaction[1]}\t{transaction[2]}\t{transaction[3]}\t{transaction[4]}\n")

        text.config(state=tk.DISABLED)

    def view_debts(self):
        debts = database.get_all_debts()
        view_window = tk.Toplevel(self.root)
        view_window.title("Список долгов")
        view_window.geometry("400x300")

        text = tk.Text(view_window)
        text.pack(expand=True, fill='both')

        text.insert(tk.END, "ID\tКлиент ID\tСумма долга\n")
        text.insert(tk.END, "-" * 50 + "\n")

        for debt in debts:
            text.insert(tk.END, f"{debt[0]}\t{debt[1]}\t{debt[2]}\n")

        text.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()