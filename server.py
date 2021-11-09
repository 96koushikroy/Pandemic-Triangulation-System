#!/usr/bin/env python

"""
Columbia's COMS W4111.003 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash
from flask_session import Session
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.152.219/proj1part2
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.152.219/proj1part2"
#
DATABASEURI = "postgresql://kr2960:dhaka3201@35.196.73.133/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#

engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (id serial, name text);""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print ("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print (request.args)


	#
	# example of a database query
	#
	cursor = g.conn.execute("SELECT name FROM test")
	names = []
	for result in cursor:
		names.append(result['name'])  # can also be accessed using result[0]
	cursor.close()

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	context = dict(data = names)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

def get_user_id(email):
	if session['privilege'] == 1:
		sql = f"select medical_id from general_users where email='{email}'"
	else:
		sql = f"select u_id from area_managers where email = '{email}'"
	cursor = g.conn.execute(sql).scalar()
	return cursor

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	name = request.form['name']
	print(name)
	# g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
	return redirect('/')


@app.route('/login', methods=['GET'])
def login():
	if session.get('logged_in') is not None:
		return redirect('/dashboard')
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
	email = request.form['email']
	password = request.form['pass']

	sql = f"select * from users where email = '{email}' and password = '{password}';"
	cursor = g.conn.execute(sql).scalar()

	if(cursor is not None):
		sql1 = f"select count(*) from area_managers where email = '{email}';"
		cursor1 = g.conn.execute(sql1).scalar()

		session['logged_in'] = True
		session['email'] = email
		session['privilege'] = 2 if cursor1 > 0 else 1 
		session['user_id'] = get_user_id(email)


		return redirect('/dashboard')
	else:
		flash('Incorrect Credentials')
		return redirect('/login')

#########
@app.route('/dashboard', methods=['GET'])
def load_dashboard():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') == 1:
		return render_template('dashboard_user.html')

###########
@app.route('/add-routine', methods=['GET'])
def load_add_routine():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	return render_template('add_routine.html')
###########

@app.route('/add-routine', methods=['POST'])
def post_add_routine():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	location = request.form['location']
	date = request.form['date']
	time = request.form['time']
	medical_id = session['user_id']

	date_time = date + ' ' + time

	sql = f"insert into routines (medical_id, location, time) values ({medical_id},'{location}','{date_time}')"
	g.conn.execute(sql)
	flash('Data Added Successfully')
	return redirect('/add-routine')
###########
@app.route('/manage-routine', methods=['GET'])
def load_manage_routine():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	medical_id = session['user_id']

	sql = f"select * from routines where medical_id = {medical_id}"
	cursor = g.conn.execute(sql)
	res = []
	for result in cursor:
		res.append({'rid': result['routine_id'],'location':result['location'], 'dt': result['time']})  # can also be accessed using result[0]
	cursor.close()
	context = dict(routines = res)
	return render_template('manage_routine.html', **context)
############
@app.route('/edit-routine/<routine_id>', methods=['GET'])
def load_edit_routine(routine_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	medical_id = session['user_id']

	sql = f"select * from routines where routine_id = {routine_id}"
	cursor = g.conn.execute(sql)
	res = []
	for result in cursor:
		date_time = (result['time']).strftime('%Y-%m-%d %H:%M').split()
		print(date_time)
		res.append({'rid': result['routine_id'],'location':result['location'], 'date': date_time[0], 'time': date_time[1]})  # can also be accessed using result[0]
	cursor.close()
	context = dict(routines = res)
	return render_template('edit_routine.html', **context)
############
@app.route('/edit-routine/<routine_id>', methods=['POST'])
def process_edit_routine(routine_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	location = request.form['location']
	date = request.form['date']
	time = request.form['time']
	medical_id = session['user_id']

	date_time = date + ' ' + time

	sql = f"update routines set location = '{location}', time = '{date_time}' where routine_id = {routine_id};"
	g.conn.execute(sql)
	flash('Record Updated Successfully')
	return redirect('/manage-routine')
############
@app.route('/delete-routine/<routine_id>', methods=['GET'])
def process_delete_routine(routine_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	medical_id = session['user_id']

	sql = f"delete from routines where routine_id = {routine_id}"
	g.conn.execute(sql)
	flash('Record Deleted Successfully')
	return redirect('/manage-routine')
############
@app.route('/logout', methods=['GET'])
def logout():
	if session.get('logged_in'):
		session.pop('logged_in')
		session.pop('email')
		flash('Logged out successfully')
	return redirect('/login')
###############
@app.route('/get-all-managers')
def get_managers():
	sql =	'select U.full_name, AM.managing_postal_code, Addr.borough\
   			from area_managers AM\
   			JOIN users U on AM.email = U.email\
   			JOIN address_management Addr on Addr.postal_code = AM.managing_postal_code;'
	
	cursor = g.conn.execute(sql)
	res = []
	for result in cursor:
		res.append({'name':result['full_name'], 'pc': result['managing_postal_code'], 'br': result['borough']})  # can also be accessed using result[0]
	cursor.close()
    
	context = dict(managers = res)
	return render_template('manager_list.html', **context)
#################

if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)

	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print ("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


# run()
