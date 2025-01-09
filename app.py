from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_socketio import SocketIO
from datetime import datetime, timedelta
import data_handler
import os
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
socketio = SocketIO(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    expenses = data_handler.get_expenses(username)
    budget = data_handler.get_budget(username)
    categories = data_handler.get_categories(username) or ["Food", "Transportation", "Entertainment", "Bills", "Other"]
    health_score = calculate_financial_health(username)
    return render_template('index.html', expenses=expenses, budget=budget, categories=categories, health_score=health_score)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        data_handler.add_user(username)
        session['username'] = username
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    amount = request.form['amount']
    category = request.form['category']
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_handler.add_expense(username, amount, category, date)
    socketio.emit('update_expenses', {'username': username})
    return redirect(url_for('home'))

@app.route('/set_budget', methods=['POST'])
def set_budget():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    budget = request.form['budget']
    data_handler.set_budget(username, budget)
    return redirect(url_for('home'))

@app.route('/delete_expense/<int:index>')
def delete_expense(index):
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    data_handler.delete_expense(username, index)
    socketio.emit('update_expenses', {'username': username})
    return redirect(url_for('home'))

@app.route('/get_expenses')
def get_expenses():
    if 'username' not in session:
        return jsonify([])
    username = session['username']
    expenses = data_handler.get_expenses(username)
    return jsonify(expenses)

@app.route('/add_category', methods=['POST'])
def add_category():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    category = request.form['category']
    data_handler.add_category(username, category)
    return redirect(url_for('home'))

@app.route('/get_forecast')
def get_forecast():
    if 'username' not in session:
        return jsonify([])
    username = session['username']
    expenses = data_handler.get_expenses(username)
    forecast = generate_forecast(expenses)
    return jsonify(forecast)

def calculate_financial_health(username):
    expenses = data_handler.get_expenses(username)
    budget = data_handler.get_budget(username)
    total_expenses = sum(expense['amount'] for expense in expenses)
    if budget == 0:
        return 50  # Default score if no budget is set
    health_score = 100 - (total_expenses / budget) * 100
    return max(0, min(100, health_score))

def generate_forecast(expenses):
    if not expenses:
        return []
    last_date = datetime.strptime(expenses[-1]['date'], "%Y-%m-%d %H:%M:%S")
    forecast = []
    for i in range(1, 31):
        date = last_date + timedelta(days=i)
        amount = random.uniform(0.8 * expenses[-1]['amount'], 1.2 * expenses[-1]['amount'])
        forecast.append({
            'date': date.strftime("%Y-%m-%d"),
            'amount': round(amount, 2)
        })
    return forecast

if __name__ == '__main__':
    socketio.run(app, debug=True)

