from flask import Flask, render_template, request, redirect, jsonify, session
import pymysql
import os
from functools import wraps
from flask_bcrypt import Bcrypt
from flask import flash

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = os.urandom(24)
db = pymysql.connect(host='127.0.0.1', user='root',database='users')

cursor = db.cursor()

#hachage du mot de passe avec le sel
def hash_password(password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed_password

#vérification du mot de passe
def check_password(input_password, stored_password):
    return bcrypt.check_password_hash(stored_password, input_password)

#mise en place du système de logging
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#rotation des fichier journaux
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=5)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html') 

@app.route('/delete_account')
def delete_account():
    return render_template('delete_account.html')  

@app.route('/maj_profil')
def maj_profil():
    return render_template('maj_profil.html') 

@app.route('/logout')
def logout():
    return render_template('logout.html') 

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')  
        return f(*args, **kwargs)
    return decorated_function

@app.route('/list')
@login_required
def list():
    cursor.execute("SELECT * FROM Utilisateurs")
    users = cursor.fetchall()

    return render_template('list.html', users=users)

@app.route('/search')
def search_users():
    search_query = request.args.get('query', '')
    sql = "SELECT * FROM Utilisateurs WHERE username LIKE %s OR name LIKE %s OR surname LIKE %s"
    cursor.execute(sql, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    users = cursor.fetchall()

    return jsonify(users)

@app.route('/register')
def register():
    return render_template('register.html') 

from flask import flash

@app.route('/register2', methods=['POST'])
def register2():
    username = request.form['username']
    name = request.form['name']
    surname = request.form['surname']
    password = request.form['password']
    email = request.form['email']
    phone = request.form['phone']

    if not is_strong_password(password):
        flash("Votre mot de passe devrait contenir au moins 8 caractères, contenir des lettres minuscules, majuscules et des chiffres.", 'error')
        return redirect('/register')

    hashed_password = hash_password(password)

    sql = "INSERT INTO Utilisateurs (username, name, surname, password, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (username, name, surname, hashed_password, email, phone)

    try:
        cursor.execute(sql, values)
        db.commit()
        flash("Registration successful! You can now log in.", 'success')
        return redirect('/login') 
    except Exception as e:
        db.rollback()
        flash("Error during registration. Please try again.", 'error')
        return redirect('/register')

def is_strong_password(password):
    return len(password) >= 8 and any(char.isupper() for char in password) and any(char.islower() for char in password) and any(char.isdigit() for char in password)

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    name = request.form['name']
    surname = request.form['surname']
    password = request.form['password']
    email = request.form['email']
    phone = request.form['phone']

    sql = "INSERT INTO Utilisateurs (username, name, surname, password, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (username, name, surname, password, email, phone)

    try:
        cursor.execute(sql, values)
        db.commit()
        return redirect('/list')  
    except Exception as e:
        db.rollback()
        return "Error: " + str(e)
@app.route('/login2', methods=['POST'])
def login2():
    entered_username = request.form['username']
    entered_password = request.form['password']

    sql = "SELECT * FROM Utilisateurs WHERE username = %s"
    cursor.execute(sql, (entered_username,))
    user = cursor.fetchone()

    if user and check_password(entered_password, user[4]):
        username = user[1]
        name = user[2]
        surname = user[3]
        password = user[4]
        email = user[5]
        phonenumber = user[6]
        admin_value = user[7]

        session['username'] = username  
        session['admin'] = admin_value 
        session['name'] = name
        session['surname'] = surname
        session['password'] = password
        session['email'] = email
        session['phonenumber'] = phonenumber

        logging.info('Utilisateur connecté avec succès : {}'.format(username))

        return redirect('/list')
    else:
        username = None
        logging.warning('Invalid credentials. Username: {}, Password: {}'.format(entered_username, entered_password))
        return "Invalid credentials. Please try again."


    

@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        sql = "DELETE FROM Utilisateurs WHERE id = %s"
        cursor.execute(sql, (user_id,))
        db.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/change_password/<int:user_id>', methods=['PUT'])
def change_password(user_id):
    try:
        data = request.get_json()
        new_password = data.get('password')

        sql = "UPDATE Utilisateurs SET password = %s WHERE id = %s"
        cursor.execute(sql, (new_password, user_id))
        db.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/upgrade_user/<user_id>', methods=['PUT'])
def upgrade_user(user_id):
    new_admin_value = 1 

    try:
        sql = "UPDATE Utilisateurs SET admin = %s WHERE id = %s"
        cursor.execute(sql, (new_admin_value, user_id))
        db.commit()

        return 'User admin level upgraded successfully', 200
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}", 500
    
@app.route('/downgrade_user/<user_id>', methods=['PUT'])
def downgrade_user(user_id):
    new_admin_value = 0 

    try:
        sql = "UPDATE Utilisateurs SET admin = %s WHERE id = %s"
        cursor.execute(sql, (new_admin_value, user_id))
        db.commit()

        return 'User admin level upgraded successfully', 200
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}", 500

@app.route('/upgrade_profil', methods=['GET', 'POST'])
def upgrade_profil():
    if 'username' in session:
        if request.method == 'POST':
            username = request.form['new_username']
            name = request.form['new_name']
            surname = request.form['new_surname']
            email = request.form['new_email']
            phone = request.form['new_phone']
            password = request.form['new_password']

            sql_select = "SELECT * FROM Utilisateurs WHERE username = %s"
            cursor.execute(sql_select, session['username'])
            user = cursor.fetchone()

            user_data = {
                'username': user[1],
                'name': user[2],
                'surname': user[3],
                'email': user[5],
                'phone': user[6],
                'password': user[4]
            }

            if username:
                user_data['username'] = username
                session['username'] = username
            if name:
                user_data['name'] = name
                session['name'] = name
            if surname:
                user_data['surname'] = surname
                session['surname'] = surname
            if email:
                user_data['email'] = email
                session['email'] = email
            if phone:
                user_data['phone'] = phone
                session['phone'] = phone
            if password:
                user_data['password'] = password
                session['password'] = password

            sql_update = "UPDATE Utilisateurs SET username = %s, name = %s, surname = %s, email = %s, phone_number = %s, password = %s WHERE username = %s"
            cursor.execute(sql_update, (user_data['username'], user_data['name'], user_data['surname'], user_data['email'], user_data['phone'], user_data['password'], session['username']))
            db.commit()

            return redirect('/list')  
        else:
            sql = "SELECT * FROM Utilisateurs WHERE username = %s"
            cursor.execute(sql, session['username'])
            user = cursor.fetchone()

            return render_template('maj_profil.html', user=user)
    else:
        return redirect('/login')  

@app.route('/logout2', methods=['POST'])
def logout2():
    session.clear()
    return redirect('/login') 

@app.route('/delete_account2', methods=['DELETE'])
def delete_account2():
    if 'username' in session:
        try:
            username = session['username']
            sql = "DELETE FROM Utilisateurs WHERE username = %s"
            cursor.execute(sql, (username,))
            db.commit()
            session.clear()
            return 'Compte utilisateur supprimé avec succès', 200
        except Exception as e:
            db.rollback()
            return f"Erreur: {str(e)}", 500
    else:
        return 'Utilisateur non connecté', 401  


if __name__ == '__main__':
    app.run(debug=True)
