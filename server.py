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
	if session.get('logged_in') is not None:
		return redirect('/dashboard')

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
	else:
		return render_template('dashboard_manager.html')

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
@app.route('/user-health-records', methods=['GET'])
def load_user_health_records():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	medical_id = session['user_id']

	sql = f"select h.r_id, d.test_name, h.medical_id, h.test_result, h.test_date_time from health_records h \
			join disease_tests d on d.d_id=h.d_id\
			where h.medical_id = {medical_id}"
	cursor = g.conn.execute(sql)
	res = []
	for result in cursor:
		res.append({'rid': result['r_id'],'test_name':result['test_name'], 'test_result': result['test_result'], 'dt': result['test_date_time']})  # can also be accessed using result[0]
	cursor.close()
	context = dict(records = res)
	return render_template('user_health_records.html', **context)
############
@app.route('/contact-trace', methods=['GET'])
def load_user_contact_traces():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 1:
		flash('Not Authorized')
		return redirect('/login')
	
	medical_id = session['user_id']

	sql_positive_cases = f"select * from health_records where test_result=True"
	cursor = g.conn.execute(sql_positive_cases)

	positive_med_ids = []
	for result in cursor:
		positive_med_ids.append(result['medical_id'])  # can also be accessed using result[0]
	cursor.close()

	contacting_emails = []

	for med_id in positive_med_ids:
		sql = f"SELECT general_users.email, R1.medical_id, R1.location, R1.time\
				 FROM  routines R1\
				 JOIN general_users ON general_users.medical_id = R1.medical_id\
				 WHERE R1.location IN\
				 (SELECT R2.location\
				 FROM routines R2\
				 WHERE R2.medical_id = {med_id})\
				 AND R1.medical_id <> {med_id}\
				 AND R1.time-(SELECT R2.time\
				 FROM routines R2\
				 WHERE R2.medical_id = {med_id} AND R2.location=R1.location) < '1 day';"
		# sql = 	"SELECT general_users.email, R1.medical_id, R1.location, R1.time\
		# 		 FROM  routines R1\
		# 		 JOIN general_users ON general_users.medical_id = R1.medical_id\
		# 		 WHERE R1.location IN\
		# 		 (SELECT R2.location\
		# 		 FROM routines R2\
		# 		 WHERE R2.medical_id = 997)\
		# 		 AND R1.medical_id <> 997\
		# 		 AND R1.time-(SELECT R2.time\
		# 		 FROM routines R2\
		# 		 WHERE R2.medical_id = 997) < '1 day';"
		cursor1 = g.conn.execute(sql)
		for result in cursor1:
			contacting_emails.append((result['email'], result['location'], result['time']))
		cursor1.close()

	traced_locations = []

	for p in contacting_emails:
		if p[0] == session['email']:
			traced_locations.append({'location': p[1], 'time': p[2]})


	context = dict(locations = traced_locations)
	return render_template('user_contact_tracing.html', **context)
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

	if not session.get('logged_in'):
		flash('Login to continue')
		return redirect('/login')

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
@app.route('/manage-health-records', methods=['GET'])
def load_health_records():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	manager_email = session['email']
	sql = f"select managing_postal_code from area_managers where email = '{manager_email}'"
	managing_postal_code = g.conn.execute(sql).scalar()
	sql1 = f"SELECT * from general_users g\
			join users u on g.email=u.email\
			join address_management a on g.address_id=a.address_id\
			where a.postal_code={managing_postal_code}"
	
	cursor = g.conn.execute(sql1)
	
	res = []
	
	for result in cursor:
		addr = result['apt'] + ', ' + result['street'] + ', ' + result['borough'] + ', ' + str(result['postal_code'])
		res.append({'medical_id':result['medical_id'], 'name':result['full_name'], 'email': result['email'], 'dob': result['dob'],'address': addr})  # can also be accessed using result[0]
	
	cursor.close()
	context = dict(records = res)
	return render_template('manage_health_records.html', **context)
###########
@app.route('/manage-health-records/<medical_id>', methods=['GET'])
def load_user_health_records_manager(medical_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	sql1 = f"SELECT h.r_id, d.test_name, h.test_result, h.test_date_time, u.email from health_records h\
			join general_users g on h.medical_id=g.medical_id\
			join users u on g.email=u.email\
			join disease_tests d on h.d_id=d.d_id\
			where h.medical_id={medical_id}"
	
	cursor = g.conn.execute(sql1)
	
	res = []
	
	for result in cursor:
		res.append({'medical_id': medical_id,'r_id':result['r_id'],'email':result['email'], 'test_name':result['test_name'], 'test_result': result['test_result'], 'test_date_time': result['test_date_time']})  # can also be accessed using result[0]
	
	cursor.close()
	context = dict(records = res)
	return render_template('manage_specific_health_records.html', **context)
###########
@app.route('/delete-health-records/<record_id>', methods=['GET'])
def process_delete_health_record(record_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 2:
		flash('Not Authorized')
		return redirect('/login')

	sql = f"delete from health_records where r_id = {record_id}"
	g.conn.execute(sql)
	flash('Record Deleted Successfully')
	return redirect(f'/manage-health-records') #fix the redirect hereee
###############
@app.route('/add-health-record/<medical_id>', methods=['GET'])
def load_add_health_record(medical_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 2:
		flash('Not Authorized')
		return redirect('/login')


	sql = f"select * from disease_tests"

	tests = []
	cursor = g.conn.execute(sql)
	for result in cursor:
		tests.append({'test_name': result['test_name'], 'd_id': result['d_id']})

	context = dict(med_id=medical_id, tests=tests)

	return render_template('add_health_record.html', **context)
###############
@app.route('/add-health-record/<medical_id>', methods=['POST'])
def process_add_health_record(medical_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 2:
		flash('Not Authorized')
		return redirect('/login')

	test_id = request.form['test_name']
	test_result = bool(request.form['test_result'])
	test_date_time = request.form['date'] + ' ' + request.form['time']

	sql1 = f"insert into health_records (medical_id, d_id, test_result, test_date_time) values ({medical_id}, {test_id}, {test_result}, '{test_date_time}')"
	g.conn.execute(sql1)
	flash('Record Added Successfully')
	return redirect(f"/add-health-record/{medical_id}")
###############
@app.route('/edit-health-records/<record_id>', methods=['GET'])
def load_edit_health_record(record_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 2:
		flash('Not Authorized')
		return redirect('/login')

	sql1 = f"SELECT h.r_id, d.d_id, d.test_name, h.test_result, h.test_date_time, u.email from health_records h\
			join general_users g on h.medical_id=g.medical_id\
			join users u on g.email=u.email\
			join disease_tests d on h.d_id=d.d_id\
			where h.r_id={record_id}"
	cursor = g.conn.execute(sql1)

	res = []
	for r in cursor:
		date_time = (r['test_date_time']).strftime('%Y-%m-%d %H:%M').split()
		res.append({'d_id': r['d_id'], 'test_name': r['test_name'], 'test_result': r['test_result'], 'date': date_time[0], 'time': date_time[1]})
	cursor.close()

	sql = f"select * from disease_tests"
	tests = []
	cursor = g.conn.execute(sql)
	for result in cursor:
		tests.append({'test_name': result['test_name'], 'd_id': result['d_id']})
	cursor.close()

	context = dict(record_id=record_id, tests=tests, record=res)
	return render_template('edit_health_records.html', **context)
#############
@app.route('/edit-health-records/<record_id>', methods=['POST'])
def process_edit_health_record(record_id):
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 2:
		flash('Not Authorized')
		return redirect('/login')

	test_id = request.form['test_name']
	test_result = bool(request.form['test_result'])
	test_date_time = request.form['date'] + ' ' + request.form['time']

	sql1 = f"update health_records set d_id={test_id}, test_result={test_result}, test_date_time='{test_date_time}' where r_id={record_id}"
	g.conn.execute(sql1)
	flash('Record Updated Successfully')
	return redirect(f"/edit-health-records/{record_id}")
###############
@app.route('/my-area-stats/', methods=['GET'])
def load_manager_area_stats():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 2:
		flash('Not Authorized')
		return redirect('/login')

	manager_email = session['email']
	sql = f"select managing_postal_code from area_managers where email = '{manager_email}'"
	managing_postal_code = g.conn.execute(sql).scalar()

	sql = f"SELECT d.test_name, h.test_result, a.street, count(*) from health_records h\
			join general_users g on h.medical_id=g.medical_id\
			join users u on g.email=u.email\
			join disease_tests d on h.d_id=d.d_id\
			join address_management a on a.address_id=g.address_id\
			where a.postal_code={managing_postal_code} and h.test_result=True\
			GROUP by d.test_name, h.test_result, a.street"

	results = []
	cursor = g.conn.execute(sql)
	for result in cursor:
		results.append({'test_name': result['test_name'], 'test_results': result['test_result'], 'street': result['street'], 'count': result['count']})

	context = dict(tests=results)

	return render_template('manager_area_stats.html', **context)
###############
@app.route('/prevalent-diseases/', methods=['GET'])
def load_prevalent_diseases():
	if not session.get('logged_in'):
		flash('Not Logged In')
		return redirect('/login')

	if session.get('privilege') != 2:
		flash('Not Authorized')
		return redirect('/login')

	sql = f"SELECT dt.test_name, count(hr.d_id)\
			FROM health_records AS hr\
			JOIN disease_tests dt ON hr.d_id=dt.d_id\
			WHERE hr.test_result = True AND hr.test_date_time > (NOW() - interval '14 days')\
			GROUP BY dt.test_name;"

	results = []
	cursor = g.conn.execute(sql)
	for result in cursor:
		results.append({'test_name': result['test_name'], 'count': result['count']})

	context = dict(tests=results)

	return render_template('prevalent_diseases.html', **context)
###############
@app.route('/signup/', methods=['GET'])
def load_signup():
	if session.get('logged_in'):
		return redirect('/dashboard')

	return render_template('general_user_signup.html')
###############
@app.route('/signup', methods=['POST'])
def process_signup():
	email = request.form['email']
	password = request.form['pass']
	medical_id = request.form['medical_id']
	dob = request.form['dob']
	full_name = request.form['fullname']
	apt = request.form['apt']
	street = request.form['street']
	borough = request.form['borough']
	postalcode = request.form['postalcode']

	sql1 = f"select count(*) from general_users where medical_id = {medical_id}"
	medCnt = g.conn.execute(sql1).scalar()
	if(medCnt > 0):
		flash('User already exists')
		return redirect('/signup')

	sql1 = f"select count(*) from users where email = '{email}'"
	userCnt = g.conn.execute(sql1).scalar()
	if(userCnt > 0):
		flash('User already exists')
		return redirect('/signup')

	sql2 = f"insert into address_management (apt, street, borough, postal_code) values ({apt}, '{street}', '{borough}', {postalcode}) RETURNING address_id"
	cursor = g.conn.execute(sql2)
	[new_id] = cursor.fetchone()

	sql3 = f"insert into users (email, password, full_name, dob) values ('{email}', '{password}', '{full_name}', '{dob}')"
	g.conn.execute(sql3)
	
	sql4 = f"insert into general_users (medical_id, email, address_id) values ({medical_id}, '{email}', {new_id})"
	g.conn.execute(sql4)

	flash('Signed up successfully')
	return redirect('/login')
###############
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
