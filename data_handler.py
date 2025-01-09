import json
from datetime import datetime

DATA_FILE = 'data.txt'

def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
            if 'categories' not in data:
                data['categories'] = {}
            return data
    except FileNotFoundError:
        return {"users": [], "expenses": {}, "budgets": {}, "categories": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=2, default=str)

def add_user(username):
    data = load_data()
    if username not in data["users"]:
        data["users"].append(username)
        data["expenses"][username] = []
        data["budgets"][username] = 0
        data["categories"][username] = ["Food", "Transportation", "Entertainment", "Bills", "Other"]
        save_data(data)

def add_expense(username, amount, category, date):
    data = load_data()
    expense = {
        "amount": float(amount),
        "category": category,
        "date": date
    }
    data["expenses"][username].append(expense)
    save_data(data)

def get_expenses(username):
    data = load_data()
    return data["expenses"].get(username, [])

def set_budget(username, budget):
    data = load_data()
    data["budgets"][username] = float(budget)
    save_data(data)

def get_budget(username):
    data = load_data()
    return data["budgets"].get(username, 0)

def delete_expense(username, index):
    data = load_data()
    if username in data["expenses"] and 0 <= index < len(data["expenses"][username]):
        del data["expenses"][username][index]
        save_data(data)

def add_category(username, category):
    data = load_data()
    if username not in data["categories"]:
        data["categories"][username] = []
    if category not in data["categories"][username]:
        data["categories"][username].append(category)
        save_data(data)

def get_categories(username):
    data = load_data()
    return data["categories"].get(username, [])

