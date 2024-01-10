from flask import Flask, render_template, request, redirect, jsonify, session
import pymysql
import os
from functools import wraps

app = Flask(__name__)

app.secret_key = os.urandom(24)
# Database connection
db = pymysql.connect(host='localhost', user='root', password='new_password', database='Users')
cursor = db.cursor()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')  # Créez ce fichier HTML pour la page de connexion

@app.route('/delete_account')
def delete_account():
    return render_template('delete_account.html')  # Créez ce fichier HTML pour la page d'inscription

@app.route('/maj_profil')
def maj_profil():
    return render_template('maj_profil.html') 

@app.route('/logout')
def logout():
    return render_template('logout.html') 

# Décorateur pour vérifier l'authentification de l'utilisateur

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')  # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
        return f(*args, **kwargs)
    return decorated_function

@app.route('/list')
@login_required
def list():
    # Fetch all users from the database
    cursor.execute("SELECT * FROM Utilisateurs")
    users = cursor.fetchall()

    return render_template('list.html', users=users)

@app.route('/search')
def search_users():
    search_query = request.args.get('query', '')

    # Fetch users based on the search query from the database
    sql = "SELECT * FROM Utilisateurs WHERE username LIKE %s OR name LIKE %s OR surname LIKE %s"
    cursor.execute(sql, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    users = cursor.fetchall()

    return jsonify(users)

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/register2', methods=['POST'])
def register2():
    username = request.form['username']
    name = request.form['name']
    surname = request.form['surname']
    password = request.form['password']
    email = request.form['email']
    phone = request.form['phone']

    # Insert data into the database
    sql = "INSERT INTO Utilisateurs (username, name, surname, password, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (username, name, surname, password, email, phone)

    try:
        cursor.execute(sql, values)
        db.commit()
        #return render_template('login.html')
        return redirect('/login')  # Redirect to login page after successful registration
    except Exception as e:
        db.rollback()
        return "Error: " + str(e)
    
@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    name = request.form['name']
    surname = request.form['surname']
    password = request.form['password']
    email = request.form['email']
    phone = request.form['phone']

    # Insert data into the database
    sql = "INSERT INTO Utilisateurs (username, name, surname, password, email, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (username, name, surname, password, email, phone)

    try:
        cursor.execute(sql, values)
        db.commit()
        #return render_template('login.html')
        return redirect('/list')  # Redirect to login page after successful registration
    except Exception as e:
        db.rollback()
        return "Error: " + str(e)

@app.route('/login2', methods=['POST'])
def login2():
    entered_username = request.form['username']
    entered_password = request.form['password']

    # Query to check credentials in the database
    sql = "SELECT * FROM Utilisateurs WHERE username = %s AND password = %s"
    cursor.execute(sql, (entered_username, entered_password))
    user = cursor.fetchone()

    if user:
        username = user[1]
        name = user[2]
        surname = user[3]
        password = user[4]
        email = user[5]
        phonenumber = user[6]
        admin_value = user[7]

        # If user exists in the database, redirect to list.html upon successful login
        session['username'] = username  # Stocker le nom d'utilisateur dans la session
        session['admin'] = admin_value 
        session['name'] = name
        session['surname'] = surname
        session['password'] = password
        session['email'] = email
        session['phonenumber'] = phonenumber

        return redirect('/list')
    else:
        return "Invalid credentials. Please try again."
    

@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Delete the user from the database based on the user_id
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

        # Update the user's password in the database based on the user_id
        sql = "UPDATE Utilisateurs SET password = %s WHERE id = %s"
        cursor.execute(sql, (new_password, user_id))
        db.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/upgrade_user/<user_id>', methods=['PUT'])
def upgrade_user(user_id):
    new_admin_value = 1  # New admin value to be set after upgrading

    try:
        # Prepare and execute SQL query to update the admin value for the specified user ID
        sql = "UPDATE Utilisateurs SET admin = %s WHERE id = %s"
        cursor.execute(sql, (new_admin_value, user_id))
        db.commit()

        return 'User admin level upgraded successfully', 200
    except Exception as e:
        db.rollback()
        return f"Error: {str(e)}", 500
    
@app.route('/downgrade_user/<user_id>', methods=['PUT'])
def downgrade_user(user_id):
    new_admin_value = 0  # New admin value to be set after upgrading

    try:
        # Prepare and execute SQL query to update the admin value for the specified user ID
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
            # Récupérer les données modifiées du formulaire
            username = request.form['new_username']
            name = request.form['new_name']
            surname = request.form['new_surname']
            email = request.form['new_email']
            phone = request.form['new_phone']
            password = request.form['new_password']

            # Récupérer les données de l'utilisateur depuis la base de données
            sql_select = "SELECT * FROM Utilisateurs WHERE username = %s"
            cursor.execute(sql_select, session['username'])
            user = cursor.fetchone()

            # Créer un dictionnaire avec les données de l'utilisateur
            user_data = {
                'username': user[1],
                'name': user[2],
                'surname': user[3],
                'email': user[5],
                'phone': user[6],
                'password': user[4]
            }

            # Mettre à jour les données de l'utilisateur dans le dictionnaire
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

            # Effectuer la mise à jour dans la base de données
            sql_update = "UPDATE Utilisateurs SET username = %s, name = %s, surname = %s, email = %s, phone_number = %s, password = %s WHERE username = %s"
            cursor.execute(sql_update, (user_data['username'], user_data['name'], user_data['surname'], user_data['email'], user_data['phone'], user_data['password'], session['username']))
            db.commit()

            # Rediriger vers une page de confirmation ou une autre page après la modification
            return redirect('/list')  # Changez '/confirmation' par votre page de confirmation
        else:
            # Récupérer les données de l'utilisateur depuis la base de données
            sql = "SELECT * FROM Utilisateurs WHERE username = %s"
            cursor.execute(sql, session['username'])
            user = cursor.fetchone()

            # Afficher les données de l'utilisateur dans le formulaire
            return render_template('maj_profil.html', user=user)
    else:
        return redirect('/login')  # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté

@app.route('/logout2', methods=['POST'])
def logout2():
    # Vider toutes les variables de session
    session.clear()
    return redirect('/login')  # Rediriger vers la page de connexion après déconnexion

@app.route('/delete_account2', methods=['DELETE'])
def delete_account2():
    if 'username' in session:
        try:
            # Récupérer le nom d'utilisateur de la session
            username = session['username']
            # Supprimer le compte de l'utilisateur connecté de la base de données
            sql = "DELETE FROM Utilisateurs WHERE username = %s"
            cursor.execute(sql, (username,))
            db.commit()
            # Déconnecter l'utilisateur après la suppression du compte
            session.clear()
            return 'Compte utilisateur supprimé avec succès', 200
        except Exception as e:
            db.rollback()
            return f"Erreur: {str(e)}", 500
    else:
        return 'Utilisateur non connecté', 401  # Non autorisé
    


if __name__ == '__main__':
    app.run(debug=True)
