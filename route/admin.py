from flask import app, flash, url_for, redirect, session, request, render_template, jsonify
import sqlite3

from app import app  # use the app from app.py

@app.before_request
def protect_admin_routes():
    protected_paths = ['/admin', '/products']
    if any(request.path.startswith(p) for p in protected_paths) and not session.get('user_id'):
        flash('You must log in first', 'warning')
        return redirect(url_for('login'))
    return None


# -----------------------
# Authentication
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('su79_database.sqlite3')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('admin/login.html')

    return render_template('admin/login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# -----------------------
# Admin Dashboard
# -----------------------
@app.route('/admin')
def admin():
    if 'user_id' not in session:
        flash('You must log in first', 'warning')
        return redirect(url_for('login'))

    conn = sqlite3.connect('su79_database.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    products_list = [dict(p) for p in products]
    return render_template('admin/index.html', products=products_list)
