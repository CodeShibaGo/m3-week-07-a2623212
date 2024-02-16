from flask import Flask, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123123123'
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)

@app.route('/setup_db')
def setup_db():
  cur = mysql.connection.cursor()
  cur.execute('CREATE DATABASE IF NOT EXISTS mydb;')
  cur.execute('USE mydb;')
  cur.execute('CREATE TABLE IF NOT EXISTS test (id INT, data VARCHAR(100));')
  cur.execute('INSERT INTO test (id, data) VALUES (1, "Hello World");')
  cur.execute('INSERT INTO test (id, data) VALUES (2, "Hello Flask");')
  cur.execute('INSERT INTO test (id, data) VALUES (3, "Hello MySQL");')
  mysql.connection.commit()
  return jsonify(success=True, message="Database and table created, data inserted")

@app.route('/query_db')
def query_db():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM test;')
    result = cur.fetchall()
    return jsonify(result)

@app.route('/')
def home():
  return '''
  <h1>Welcome to the Flask MySQL App</h1>
  <ul>
    <li><a href="/setup_db">Setup Database</a></li>
    <li><a href="/query_db">Query Database</a></li>
  </ul>
  '''