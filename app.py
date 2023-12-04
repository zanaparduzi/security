from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')  # Créez ce fichier HTML pour la page de connexion

@app.route('/delete_account')
def delete_account():
    return render_template('delete_account.html')  # Créez ce fichier HTML pour la page d'inscription

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/maj_profil')
def maj_profil():
    return render_template('maj_profil.html') 

@app.route('/logout')
def logout():
    return render_template('logout.html') 

@app.route('/list')
def list():
    return render_template('list.html') 

if __name__ == '__main__':
    app.run(debug=True)
