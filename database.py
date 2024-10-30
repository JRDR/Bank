import sqlite3
from datetime import datetime
from docx import Document

def init_db():
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            contract_number TEXT NOT NULL,
            contract_type TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            status TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            amount REAL,
            transaction_type TEXT,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_debts_and_statuses():
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.id, c.name, a.status, SUM(t.amount) AS total_debt
        FROM clients c
        LEFT JOIN accounts a ON c.id = a.client_id
        LEFT JOIN transactions t ON c.id = t.client_id AND t.transaction_type = 'долг'
        GROUP BY c.id, c.name, a.status
    ''')
    
    debts = cursor.fetchall()
    conn.close()
    return debts

def add_client(name, phone, email):
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clients (name, phone, email) VALUES (?, ?, ?)
    ''', (name, phone, email))
    conn.commit()
    conn.close()

def get_all_clients():
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients")
    clients = cursor.fetchall()
    conn.close()
    return clients

def generate_contract(client_id, contract_number, contract_type):
    client = get_client(client_id)
    
    if contract_type == "Договор на оказание услуг":
        template_path = "service_agreement_template.docx"
        status = "открытый"
    elif contract_type == "Договор на прекращение оказания услуг":
        template_path = "termination_agreement_template.docx"
        status = "закрытый"
    elif contract_type == "Договор на займ":
        template_path = "loan_agreement_template.docx"
        status = "открытый"
        debt_amount = 50000  # или передать как параметр
        add_transaction(client_id, debt_amount, "долг")
    else:
        raise ValueError("Неизвестный тип договора")
    
    document = Document(template_path)
    
    for paragraph in document.paragraphs:
        if '{{name}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{name}}', client['name'])
        if '{{phone}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{phone}}', client['phone'])
    
    file_name = f"{contract_type}_{contract_number}.docx"
    document.save(file_name)

    # Обновляем счет
    update_account_status(client_id, status)

    return file_name

def add_transaction(client_id, amount, transaction_type):
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    
    # Получение текущей даты
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO transactions (client_id, amount, transaction_type, date)
        VALUES (?, ?, ?, ?)
    ''', (client_id, amount, transaction_type, current_date))
    
    conn.commit()
    conn.close()
    
def update_account_status(client_id, status):
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO accounts (client_id, status) VALUES (?, ?)
    ''', (client_id, status))
    conn.commit()
    conn.close()

def get_all_contracts():
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contracts")
    contracts = cursor.fetchall()
    conn.close()
    return contracts

def get_client(client_id):
    conn = sqlite3.connect("client_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    conn.close()
    return client