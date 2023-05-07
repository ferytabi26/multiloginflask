from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from flask_socketio import SocketIO, emit
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

offset = 0

app = Flask(__name__)
app.secret_key = 'bebasapasaja'
socketio = SocketIO(app)
#koneksi
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="robodc_test",
    autocommit=True 
    # barang penting ini autocommit=True 
)

#index
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

# def get_data():
#     mycursor = mydb.cursor()
#     query = "SELECT * FROM sensor"
#     mycursor.execute(query)
#     rows = mycursor.fetchall()
#     mycursor.close()
#     def serialize_datetime(row):
#         row = list(row)
#         for i, val in enumerate(row):
#             if isinstance(val, datetime.datetime):
#                 row[i] = val.strftime('%Y-%m-%d %H:%M:%S')
#         return row

#     rows = [serialize_datetime(row) for row in rows]
#     return rows

@app.route('/controller')
def controller():
    mycursor = mydb.cursor()
    query = "SELECT * FROM sensor ORDER BY id DESC LIMIT 4"
    mycursor.execute(query)
    rows = mycursor.fetchall()
    mycursor.close()
    return render_template('controller.html',data=rows)

@socketio.on('get_new_data')
def handle_new_data():
    mycursor = mydb.cursor()
    query = "SELECT * FROM sensor ORDER BY id DESC LIMIT 4"
    mycursor.execute(query)
    rows = mycursor.fetchall()
    mycursor.close()
    def serialize_datetime(row):
        row = list(row)
        for i, val in enumerate(row):
            if isinstance(val, datetime.datetime):
                row[i] = val.strftime('%Y-%m-%d %H:%M:%S')
        return row

    rows = [serialize_datetime(row) for row in rows]
    emit('new_data', {'data': rows})

@app.route('/get_new_data_tambah')
def get_new_data_tambah():
    global offset
    offset += 10
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM sensor ORDER BY id DESC LIMIT 10 OFFSET %s",[offset])
    rows = mycursor.fetchall()
    mycursor.close()
    print(rows)
    return render_template('history.html',data=rows)


@app.route('/get_new_data_kurang')
def get_new_data_kurang():
    global offset
    offset -= 10
    if offset<10:
        offset = 0
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM sensor ORDER BY id DESC LIMIT 10")
        rows = mycursor.fetchall()
        mycursor.close()
        return render_template('history.html',data=rows)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM sensor ORDER BY id DESC LIMIT 10 OFFSET %s",[offset])
    rows = mycursor.fetchall()
    mycursor.close()
    return render_template('history.html',data=rows)

#registrasi
@app.route('/registrasi', methods=('GET','POST'))
def registrasi():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        #cek username atau email
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM robodc_table WHERE username=%s OR email=%s',(username, email, ))
        akun = mycursor.fetchone()
        if akun is None:
            mycursor.execute('INSERT INTO robodc_table VALUES (NULL, %s, %s, %s)', (username, email, generate_password_hash(password)))
            mydb.commit()
            flash('Registrasi Berhasil','success')
        else :
            flash('Username atau email sudah ada','danger')
    return redirect(request.referrer)

#login
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        #cek data username
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM robodc_table WHERE email=%s',(email, ))
        akun = mycursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek Username Anda','danger')
        elif not check_password_hash(akun[3], password):
            flash('Login gagal, Cek Password Anda', 'danger')
        elif not email or not password:
            session['loggedin'] = False
        else:
            session['loggedin'] = True
            session['username'] = akun[1]
            return redirect(url_for('index'))
    return render_template('login_page.html')

@app.route('/history')
def history():
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM sensor ORDER BY id DESC LIMIT 10 OFFSET %s",[offset])
    rows = mycursor.fetchall()
    mycursor.close()
    print(rows)
    return render_template('history.html',data=rows)

#logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)