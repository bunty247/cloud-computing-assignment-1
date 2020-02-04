import sqlite3
import os
from flask import Flask, render_template, request, g, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from collections import Counter

app = Flask(__name__, static_folder='/static')

DATABASE = '/home/abhishek/Desktop/Abhishek/UC/CS6065-Cloud_Computing/Assignment1/flaskApp/dbFile/cloud_assign.db'
UPLOAD_FOLDER = '/home/abhishek/Desktop/Abhishek/UC/CS6065-Cloud_Computing/Assignment1/flaskApp/fileUpload'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config.from_object(__name__)

def connect_to_database():
	return sqlite3.connect(app.config['DATABASE'])

def get_db():
	db = getattr(g, 'db', None)
	if db is None:
		db = g.db = connect_to_database()
	return db

@app.teardown_appcontext
def close_connection(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

def execute_query(query, args=()):
	print("Executing... : " + query)
	print(args)
	db = get_db()
	curr = db.cursor()
	rows = curr.execute(query, args).fetchall()
	db.commit()
	return rows

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def readFile(file):
	file = open(file, 'r')
	file_dict = {}
	file_content = ''
	for word in file.read():
		if word.isalpha():
			if word in file_dict:
				file_dict[word] = file_dict.get(word) + 1
			else:
				file_dict[word] =  1

	for item in file_dict.items():
		file_content += "{}:{}\t".format(*item)
	return file_content

@app.route('/')
def goToIndex():
	return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	password = request.form['password']
	query = """SELECT * from USER_DATA where USERNAME = ? and PASSWORD = ?"""
	result = execute_query(query, [username, password])
	print(result)
	if(len(result) > 0):
		query = """SELECT FILE_NAME, FILE_CONTENT from USER_FILE where USERNAME = ?"""
		file_list = execute_query(query, [username])
		values = [result[0][0], result[0][2], result[0][3], result[0][4]]
		return render_template('info_page.html', values = values, files = file_list)
	else:
		error = "Invalid Username or password"
		return render_template('index.html', error = error)

@app.route('/register', methods=['POST'])
def register():
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email_id = request.form['email_id']
	
	query = """SELECT * from USER_DATA where USERNAME = ?"""
	result = execute_query(query, [username])
	if(len(result) > 0):
		error = "Username already in use"
		return render_template('index.html', error = error)
	else:
		try:
			query = """INSERT INTO USER_DATA (USERNAME, PASSWORD, FIRST_NAME, LAST_NAME, EMAIL_ID) values (?, ?, ?, ?, ?)"""
			values = [username, password, first_name, last_name, email_id]
			execute_query(query, values)
			values = [username, first_name, last_name, email_id]
			return render_template('info_page.html', values = values)
		except sqlite3.OperationalError as e:
			print(e)

@app.route('/uploadFile', methods=['POST'])
def uploadFile():
	print(request.files)
	if 'file' not in request.files:
		query = """SELECT FILE_NAME, FILE_CONTENT from USER_FILE where USERNAME = ?"""
		file_list = execute_query(query, [request.form['username']])
		info_page_details = [request.form['username'], request.form['first_name'], request.form['last_name'], request.form['email_id']]
		error = 'File not selected'
		return render_template('info_page.html', values = info_page_details, files = file_list, error = error)
	file = request.files['file']
	if file == '':
		query = """SELECT FILE_NAME, FILE_CONTENT from USER_FILE where USERNAME = ?"""
		file_list = execute_query(query, [request.form['username']])
		info_page_details = [request.form['username'], request.form['first_name'], request.form['last_name'], request.form['email_id']]
		error = 'File not selected'
		return render_template('info_page.html', values = info_page_details, files = file_list, error = error)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		file_content = readFile(app.config['UPLOAD_FOLDER'] + '/' + filename)
		query = """INSERT INTO USER_FILE (USERNAME, FILE_NAME, FILE_CONTENT) values (?, ?, ?)"""
		values = [request.form['username'], filename, file_content]
		execute_query(query, values)
		query = """SELECT FILE_NAME, FILE_CONTENT from USER_FILE where USERNAME = ?"""
		file_list = execute_query(query, [request.form['username']])
		info_page_details = [request.form['username'], request.form['first_name'], request.form['last_name'], request.form['email_id']]
		return render_template('info_page.html', values = info_page_details, files = file_list)

if __name__ == '__main__':
	app.run()
