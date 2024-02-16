from flask import Flask, jsonify,render_template,request
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from MySQLdb.cursors import DictCursor

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123123123'
app.config['MYSQL_DB'] = 'mydb'

mysql = MySQL(app)

# Models
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product = db.Column(db.String(64))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup_db')
def setup_db():
  cur = mysql.connection.cursor()

  cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(50) NOT NULL,
      email VARCHAR(255) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  ''')

  cur.execute('''
    CREATE TABLE IF NOT EXISTS orders (
      id INT AUTO_INCREMENT PRIMARY KEY,
      user_id INT NOT NULL,
      product VARCHAR(50) NOT NULL,
      quantity INT NOT NULL,
      price DECIMAL(10, 2) NOT NULL,
      ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  ''')

  cur.execute('''
    INSERT INTO users (username, email)
    VALUES ('user1', 'user1@example.com'), ('user2', 'user2@example.com')
  ''')

  cur.execute("SELECT id FROM users WHERE username IN ('user1', 'user2')")
  user_ids = [row[0] for row in cur.fetchall()]

  for user_id in user_ids:
    cur.execute('''
      INSERT INTO orders (user_id, product, quantity, price)
      VALUES (%s, 'product1', 1, 9.99), (%s, 'product2', 2, 19.99)
    ''', (user_id, user_id))

  mysql.connection.commit()
  cur.close()

  return 'Database setup completed.'

@app.route('/orders')
def get_orders_by_user_id():
    user_id = request.args.get('user_id')
    cur = mysql.connection.cursor(DictCursor)
    cur.execute('''
        SELECT orders.*
        FROM orders
        WHERE orders.user_id = %s
    ''', (user_id,))
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/clear_db')
def clear_db():
  cur = mysql.connection.cursor()

  # 刪除 order 表
  cur.execute('DROP TABLE IF EXISTS `orders`')

  # 刪除 user 表
  cur.execute('DROP TABLE IF EXISTS users')

  mysql.connection.commit()
  cur.close()

  return 'Database cleared.'