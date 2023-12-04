from flask import Flask, render_template, request, redirect, jsonify
import pymysql

app = Flask(__name__)

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

@app.route('/list')
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

@app.route('/login2', methods=['POST'])
def login2():
    entered_username = request.form['username']
    entered_password = request.form['password']

    # Query to check credentials in the database
    sql = "SELECT * FROM Utilisateurs WHERE username = %s AND password = %s"
    cursor.execute(sql, (entered_username, entered_password))
    user = cursor.fetchone()

    if user:
        # If user exists in the database, redirect to list.html upon successful login
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

if __name__ == '__main__':
    app.run(debug=True)
