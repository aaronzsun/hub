# created by Aaron Sun | last updated 12/8/19 at 8:49 PM
# imports necessary libraries
from flask import Flask, request, render_template, redirect, session, flash
from flask_session import Session
import os
import mysql.connector
from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

# creates flask app
app = Flask(__name__)

# sets secret key
app.secret_key = os.urandom(24)

# from cs50 finance
app.config["TEMPLATES_AUTO_RELOAD"] = True

# from cs50 finance
@app.after_request
def after_request(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	response.headers["Expires"] = 0
	response.headers["Pragma"] = "no-cache"
	return response

# from cs50 finance
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# connects to local mySQL database
database = mysql.connector.connect(
		host="remotemysql.com",
		user="nmtZXktUYG",
		passwd="***********",
		database="nmtZXktUYG"
	)

# sets database as db
db = database.cursor(buffered=True)

# login required, conceptualized from cs50 finance
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if "user_id" in session:
			return f(*args, **kwargs)
		else:
			return redirect("/login")  # if user_id is not in session (not logged in), redirects to login page
	return wrap

# index route, requires login: home page with recent posts
@app.route("/")
@login_required
def index():
	id = session["user_id"]  # gets session id
	db.execute("SELECT init FROM users WHERE id = %(id)s", {"id": id})  # calls DB to check if information has been initialized
	infoBool = db.fetchall()  # gets result of query
	infoBool = infoBool[0][0]  # gets init variable from query
	if infoBool == 0:  # if information has not been initialized, redirects to initialization page
		return redirect("/init")
	else:  # if information has been initialized
		db.execute("SELECT username, posttime, posttext FROM posts WHERE poster_id IN (SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1) OR poster_id IN (SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1) OR poster_id = %(id)s ORDER BY post_id DESC",
					{"id": id})  # gets post information from friends, ordered in chronological order
		feed = db.fetchall()  # gets result of query

		return render_template("index.html", feed=feed)  # renders index template with feed

# viewprofile route, requires login: used to view other user profiles
@app.route("/viewprofile")
@login_required
def viewprofile():
	id = session["view_id"]  # gets session id
	db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": id})  # gets username
	username = db.fetchall()
	username = username[0][0]

	db.execute("SELECT first FROM info WHERE info_id = %(id)s", {"id": id})  # gets first name
	first = db.fetchall()
	if not len(first) == 0:  # NULL check
		first = first[0][0]
	else:
		first = ""

	db.execute("SELECT last FROM info WHERE info_id = %(id)s", {"id": id})  # gets last name
	last = db.fetchall()
	if not len(last) == 0:  # NULL check
		last = last[0][0]
	else:
		last = ""

	db.execute("SELECT bio FROM info WHERE info_id = %(id)s", {"id": id})  # gets biography
	bio = db.fetchall()
	if not len(bio) == 0:  # NULL check
		bio = bio[0][0]
	else:
		bio = "No Biography Yet!"

	db.execute("SELECT * FROM media WHERE media_id = %(id)s", {"id": id})  # gets social media information from user
	media = db.fetchall()
	media = media[0]
	myMedia = []

	if not len(media) == 0:
		for i in range(len(media) - 1):  # cycles through media links
			if media[i] is None:
				if i == 0:
					myMedia.append("No Facebook Information Added.")  # NULL check for social media handles
				elif i == 1:	
					myMedia.append("No Instagram Information Added.")
				elif i == 2:
					myMedia.append("No Twitter Information Added.")
				elif i == 3:
					myMedia.append("No LinkedIn Information Added.")
			else:
				myMedia.append(media[i])  # if not NULL, append to media information

	# returns viewprofile template with users information and media
	return render_template("viewprofile.html", username=username, first=first, last=last, bio=bio, media=myMedia)

# friends route, requires login: used to look at user's current friend list
@app.route("/friends", methods=["GET","POST"])
@login_required
def friends():
	if request.method == "POST":  # if post method (changes made)
		id = session["user_id"]

		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends where user received request
		list1 = db.fetchall()

		db.execute("SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends where user sent request
		list2 = db.fetchall()

		friendlist = []  # initializes friendlist

		for i in list1:  # cycles through first query ids and gets the username, appending them to friendlist
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		for i in list2:  # cycles through second query ids and gets the username, appending them to friendlist
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		for friend in friendlist:  # cycles through friendlist to create customized pathways to view each friend's profile 
			db.execute("SELECT id FROM users WHERE username = %(username)s", {"username": friend})
			friend_id = db.fetchall()
			friend_id = friend_id[0][0]  # gets id of friend

			if request.form.get(friend) == "viewprof":  # if viewprofile was clicked, redirects to viewprofile
				session["view_id"] = friend_id
				return redirect("/viewprofile")

			if request.form.get(friend) == "unfriend":  # if unfriend was clicked, queries DB to remove friend
				db.execute("DELETE FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(id)s",
							{"sender": friend_id, "id": id})
				db.execute("DELETE FROM friends WHERE sender_id = %(id)s AND receiver_id = %(receiver)s",
							{"receiver": friend_id, "id": id})
				database.commit()  # commits changes to the database

				message = str(friend) + " has been removed from your friends list"  # sets message for flash

		flash(message)  # shows message at top of screen on rendering
		return redirect("/")  # renders original template
	else:  # if not post method
		id = session["user_id"]

		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends in identical fashion to above
		list1 = db.fetchall()

		db.execute("SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends in identical fashion to above
		list2 = db.fetchall()

		friendlist = []  # initializes friendlist

		for i in list1:  # cycles through first query and gets usernames to append
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		for i in list2:  # cycles through second query and gets usernames to append
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		return render_template("friends.html", friendlist=friendlist)  # returns friends.html with list of friends usernames for display

# profile route, login required: used to view your own profile
@app.route("/profile")
@login_required
def profile():
	id = session["user_id"]
	db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": id})  # queries DB for username
	username = db.fetchall()
	username = username[0][0]

	db.execute("SELECT first FROM info WHERE info_id = %(id)s", {"id": id})  # queries DB for first name
	first = db.fetchall()
	if not len(first) == 0:  # NULL check
		first = first[0][0]
	else:
		first = ""

	db.execute("SELECT last FROM info WHERE info_id = %(id)s", {"id": id})  # queries DB for last name
	last = db.fetchall()
	if not len(last) == 0:  # NULL check
		last = last[0][0]
	else:
		last = ""

	db.execute("SELECT bio FROM info WHERE info_id = %(id)s", {"id": id})  # queries DB for bio
	bio = db.fetchall()
	if not len(bio) == 0:  # NULL check
		bio = bio[0][0]
	else:
		bio = "No Biography Yet!"

	db.execute("SELECT * FROM media WHERE media_id = %(id)s", {"id": id})  # queries DB for social media
	media = db.fetchall()
	media = media[0]
	myMedia = []

	if not len(media) == 0:
		for i in range(len(media) - 1):
			if media[i] is None:
				if i == 0:
					myMedia.append("No Facebook Information Added.")  # NULL check for social media handles
				elif i == 1:
					myMedia.append("No Instagram Information Added.")
				elif i == 2:
					myMedia.append("No Twitter Information Added.")
				elif i == 3:
					myMedia.append("No LinkedIn Information Added.")
			else:
				myMedia.append(media[i])  # if not null, appends

	# returns profile template with information
	return render_template("profile.html", username=username, first=first, last=last, bio=bio, media=myMedia)

# edit route, login required: allows users to edit their profile information
@app.route("/edit", methods = ["GET", "POST"])
@login_required
def edit():
	if request.method == "POST":  # if post method
		id = session["user_id"]
		db.execute("SELECT * FROM users WHERE id = %(id)s", {"id": id})  # gets user info
		rows = db.fetchall()

		if not check_password_hash(rows[0][2], request.form.get("password")):  # checks to make sure password is valid
			flash("Invalid Password.")
			return redirect("/edit")
		else:
			username = request.form.get("username")  # gets information from edit form
			first = request.form.get("first")
			last = request.form.get("last")
			bio = request.form.get("bio")
			fb = request.form.get("fb")
			ig = request.form.get("ig")
			twit = request.form.get("twit")
			link = request.form.get("link")

		db.execute("UPDATE users SET username = %(username)s WHERE id = %(id)s", {"username": username, "id": id})  # queries DB to update inputed information
		db.execute("UPDATE info SET first = %(first)s, last = %(last)s, bio = %(bio)s WHERE info_id = %(id)s", 
						{"first": first, "last": last, "bio": bio, "id": id})
		db.execute("UPDATE media SET fb = %(fb)s, ig = %(ig)s, twit = %(twit)s, link = %(link)s WHERE media_id = %(id)s",
						{"fb": fb, "ig": ig, "twit": twit, "link": link, "id": id})
		database.commit()  # commits changes to database

		flash("Your profile information has been saved.")  # flashes confirmation message
		return redirect("/")  # redirects to index
	else:  # if not post
		id = session["user_id"]
		db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": id})  # gets user information for placeholders in input fields
		username = db.fetchall()
		username = username[0][0]  # gets username


		db.execute("SELECT first FROM info WHERE info_id = %(id)s", {"id": id})  # gets first name
		first = db.fetchall()
		if not len(first) == 0:  # NULL check
			first = first[0][0]
		else:
			first = ""

		db.execute("SELECT last FROM info WHERE info_id = %(id)s", {"id": id})  # gets last name
		last = db.fetchall()
		if not len(last) == 0:  # NULL check
			last = last[0][0]
		else:
			last = ""

		db.execute("SELECT bio FROM info WHERE info_id = %(id)s", {"id": id})  # gets bio
		bio = db.fetchall()
		if not len(bio) == 0:  # NULL check
			bio = bio[0][0]
		else:
			bio = "No Biography Yet!"

		db.execute("SELECT * FROM media WHERE media_id = %(id)s", {"id": id})  # gets media
		media = db.fetchall()
		media = media[0]
		myMedia = []

		print(len(media))
		if not len(media) == 0:
			for i in range(len(media) - 1):
				if media[i] is None:
					if i == 0:
						myMedia.append("No Facebook Information Added.")  # NULL check for media
					elif i == 1:
						myMedia.append("No Instagram Information Added.")
					elif i == 2:
						myMedia.append("No Twitter Information Added.")
					elif i == 3:
						myMedia.append("No LinkedIn Information Added.")
				else:
					myMedia.append(media[i])  # if not null, appends

		# displays edit form with prefilled information of user
		return render_template("edit.html", user=username, first=first, last=last, bio=bio, media=myMedia)

# post route, login required: allows users to make posts visible to their friends
@app.route("/post", methods=["GET","POST"])
@login_required
def post():
	if request.method == "POST":  # if post method
		my_id = session["user_id"]
		db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": my_id})  # gets username
		username = db.fetchall()
		username = username[0][0]

		time = datetime.datetime.now()  # gets current time using datetime
		text = str(request.form.get("mypost"))  # gets post text
		sendTo = request.form.get("postOptions")  # gets recepient information

		if sendTo == "all":  # if to be sent to all
			db.execute("INSERT INTO posts (posttext, poster_id, posttime, username) VALUES (%(text)s, %(id)s, %(time)s, %(user)s)", 
						{"text": text, "id": my_id, "time": time, "user": username})  # inserts into post database
			database.commit()  # commits changes
		else:
			id = my_id  # sets id to my_id for context of following code

			db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends in identical fashion to above
			list1 = db.fetchall()

			db.execute("SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends in identical fashion to above
			list2 = db.fetchall()

			friendlist = []  # initializes friendlist

			for i in list1:  # cycles through first query and gets usernames to append
				friend_id = int(i[0])
				db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
				friend_user = db.fetchall()
				friend_user = friend_user[0][0]
				friendlist.append(friend_user)

			for i in list2:  # cycles through second query and gets usernames to append
				friend_id = int(i[0])
				db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
				friend_user = db.fetchall()
				friend_user = friend_user[0][0]
				friendlist.append(friend_user)

			for friend in friendlist:
				if sendTo == friend:
					db.execute("SELECT id FROM users WHERE username = %(username)s", {"username": friend})
					friend_id = db.fetchall()
					friend_id = friend_id[0][0]

					db.execute("INSERT INTO messages (text, receiver_id, sender_id, msgtime, sender_user) VALUES (%(text)s, %(receiver_id)s, %(id)s, %(time)s, %(user)s)",
								{"text": text, "receiver_id": friend_id, "id": id, "time": time, "user": username})
					database.commit()

		flash("Your message has been posted.")  # flashes confirmation message

		return render_template("post.html")  # returns empty post template
	else:
		id = session["user_id"]

		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends in identical fashion to above
		list1 = db.fetchall()

		db.execute("SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1", {"id": id})  # gets list of friends in identical fashion to above
		list2 = db.fetchall()

		friendlist = []  # initializes friendlist

		for i in list1:  # cycles through first query and gets usernames to append
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		for i in list2:  # cycles through second query and gets usernames to append
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		return render_template("post.html", friendlist=friendlist)  # returns empty post template

# add route, login required: allows users to search for other users and add or view their profiles
@app.route("/add", methods=["GET","POST"])
@login_required
def add():
	if request.method == "POST":  # if post method
		if request.form.get("button") == "search":  # if search button was clicked
			search = request.form.get("search")  # gets inputed username
			search = "%" + search + "%"  # creates string for LIKE query
			db.execute("SELECT username FROM users WHERE LOWER(username) LIKE LOWER(%(search)s)", {"search": search})  # searches database
			result = db.fetchall()
			resultlist = []  # initializes result list
			
			if len(result) == 0:  # if no results returned
				flash("Sorry, no results found.")
				return render_template("add.html", resultlist = resultlist)
			else:
				for user in result:  # cycles through result and appends username to resultlist
					holder = user[0]
					resultlist.append(holder)
					session["search_list"] = resultlist  # stores result list in session for reload on render_template
				return render_template("add.html", resultlist = resultlist)

		resultlist = session["search_list"]  # gets result list in session for reload on render_template

		for user in resultlist:  # cycles through resultlist to create customized pathways
			if request.form.get(str(user)) == "add":  # if add button clicked
				my_id = session["user_id"]  
				result = user  # gets username of result
				db.execute("SELECT id FROM users WHERE LOWER(username) = %(result)s", {"result": result})  # gets id of user
				request_id = db.fetchall()
				request_id = request_id[0][0]

				if my_id == request_id:  # check to make sure user did not request themself
					flash("You can't friend request yourself.")  # flashes error message
					return redirect("/add")

				db.execute("SELECT * FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(receiver)s", {"sender": my_id, "receiver": request_id})
				check = db.fetchall()  # checks to make sure request has not already been sent

				db.execute("SELECT * FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(receiver)s", {"sender": request_id, "receiver": my_id})
				check2 = db.fetchall()  # checks to make sure request has not already been received

				message = ""

				if len(check) == 0 and len(check2) == 0:  # if check is passed
					db.execute("INSERT INTO friends (sender_id, receiver_id) VALUES (%(sender)s, %(receiver)s)", {"sender": my_id, "receiver": request_id})
					database.commit()  # adds request to database
					message = "A friend request has been sent to " + result  # sets confirmation message for flash
				else:
					if len(check) == 0:  # if check failed
						accepted2 = check2[0][2]
						if accepted2 == 0:
							message = "You already have a request from " + result  # sets error message
						else:
							message = "You are already friends with " + result  # sets error message
					elif len(check2) == 0:  # if check failed
						accepted = check[0][2]
						if accepted == 0:
							message = "A request has already been sent to " + result  # sets error message
						else:
							message = "You are already friends with " + result	# sets error message
						
				flash(message)  # flashes message
				return redirect("/add")  # redirects for refresh

			elif request.form.get(str(user)) == "viewprof":  # if view profile was selected
				result = user
				db.execute("SELECT id FROM users WHERE LOWER(username) = %(result)s", {"result": result})  # gets id of profile
				prof_id = db.fetchall()
				prof_id = prof_id[0][0]
				session["view_id"] = prof_id  # stores id of profile

				return redirect("/viewprofile")  # redirects to viewprofile with prof_id stored
	else:  # if get method
		return render_template("add.html")

# init route, login required: used to initialize information for user before they can use the website
@app.route("/init", methods=["GET","POST"])
@login_required
def init():
	if request.method == "POST":  # if post method
		id = session["user_id"]
		first = request.form.get("first")  # gets information from form
		last = request.form.get("last")
		bio = request.form.get("bio")

		db.execute("UPDATE info SET first = %(first)s, last = %(last)s, bio = %(bio)s WHERE info_id = %(id)s", 
						{"first": first, "last": last, "bio": bio, "id": id})  # updates information in database
		database.commit()  # commits info to database

		db.execute("UPDATE users SET init = 1 WHERE id = %(id)s", {"id": id})  # updates init status
		database.commit()  # commits info to database

		return redirect("/")  # redirects back to index
	else:  # get method
		return render_template("init.html")  # renders init information template

# mail route, login required: shows friend requests
@app.route("/mail", methods=["GET","POST"])
@login_required
def mail():
	if request.method == "POST":  # if post method
		my_id = session["user_id"]
		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 0", {"id": my_id})  # gets requests from database
		requestList = db.fetchall()
		myRequests = []  # initializes myrequests

		for requests in requestList:
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": requests[0]})  # gets username of requesters
			holder = db.fetchall()[0]
			myRequests.append(holder)

		message = ""  # initializes message for flash

		for requests in myRequests:  # cycles through myrequests to make individualized pathways
			db.execute("SELECT id FROM users WHERE username = %(username)s", {"username": requests[0]})  # gets ID
			sender_id = db.fetchall()
			sender_id = sender_id[0][0]  # gets sender ID

			if request.form.get(str(requests[0])) == "accept":  # if accept is clicked
				db.execute("UPDATE friends SET accepted = 1 WHERE sender_id = %(sender)s AND receiver_id = %(id)s",  # updates database
							{"sender": sender_id, "id": my_id})
				database.commit()  # commits info
				message = str(requests[0]) + "'s friend request has been accepted"  # sets message for flash
			if request.form.get(str(requests[0])) == "reject":  # if reject is clicked
				db.execute("DELETE FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(id)s",  # updates database
							{"sender": sender_id, "id": my_id})
				database.commit()  # commits info
				message = str(requests[0]) + "'s friend request has been rejected"  # sets message for flash

		flash(message)  # flashes message at top of screen
		return redirect("/mail")  # returns mail page
	else:
		my_id = session["user_id"]
		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 0", {"id": my_id})  # gets requests from database
		requestList = db.fetchall()
		myRequests = []  # initializes myrequests

		for requests in requestList:
			print(requests)
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": requests[0]})  # gets usernames of requesters for display
			holder = db.fetchall()[0]
			myRequests.append(holder)

		db.execute("SELECT text, sender_user, msgtime FROM messages WHERE receiver_id = %(id)s ORDER BY msgtime DESC", {"id": my_id})
		myMessages = db.fetchall()

		return render_template("mail.html", myList = myRequests, messages=myMessages)  # displays mail with list of requests

# login route: used for users to login
@app.route("/login", methods=["GET","POST"])
def login():
	if request.method == "POST":  # if post method
		if request.form["button"] == "register":  # if register is clicked, redirect to register route
			return redirect("/register")
		if request.form["button"] == "login":  # if login is clicked
			db.execute("SELECT * FROM users WHERE username = %(username)s", {"username": request.form.get("username")})  # searches for user using username
			rows = db.fetchall()

			if len(rows) == 0:  # if no results returned
				flash("Invalid Username.")
				return render_template("login.html")  # refreshes with invalid username flash
			if not check_password_hash(rows[0][2], request.form.get("password")):  # if results are returned, checks password
				flash("Invalid Password.")  # sets password error message
				return render_template("login.html")

			session["user_id"] = rows[0][0]  # sets session for login

			return redirect("/")  # redirects to index
	else:  # if get method
		return render_template("login.html")  # renders login screen

# logout route, login required: used for users to logout
@app.route("/logout")
@login_required
def logout():
	session.clear()  # clears session and redirects to login page
	return redirect("/login")
    
# register route: used for users to create accounts
@app.route("/register", methods=["GET","POST"])
def register():
	if request.method == "POST":
		if not request.form.get("password") == request.form.get("confirmation"):  # if passwords are not the same, returns error
			flash("Your passwords do not match.")  # flashes error
			return render_template("register.html")

		pwHash = generate_password_hash(request.form.get("password"))  # gets hash of password for database storage

		db.execute("SELECT username FROM users WHERE username = %(username)s", {"username": request.form.get("username")})  # queries database for username
		userCheck = db.fetchall()

		if len(userCheck) == 0:  # if username isn't taken
			newUser = db.execute("INSERT INTO users (username, password) VALUES (%(username)s, %(pw)s)", {'username': request.form.get("username"), "pw": pwHash})
			database.commit()  # updates username and commits info
		else:
			flash("Sorry, that username is already taken.")  # flashes message if username is taken
			return render_template("register.html")

		db.execute("SELECT * FROM users WHERE username = %(username)s", {"username": request.form.get("username")})  # gets id from db
		rows = db.fetchall()

		session["user_id"] = rows[0][0]  # sets session to user_id

		db.execute("INSERT INTO info (info_id) VALUES (%(id)s)", {'id': session["user_id"]})  # initializes info row for user
		database.commit()

		db.execute("INSERT INTO media (media_id) VALUES (%(id)s)", {'id': session["user_id"]})  # initializes media row for user
		database.commit()

		return redirect("/")  # redirects to index
	else:  # if get method
		return render_template("register.html")  # returns register template

# from cs50 finance
def errorhandler(e):
	if not isinstance(e, HTTPException):
		e = InternalServerError()
	return render_template("error.html")

for code in default_exceptions:
	app.errorhandler(code)(errorhandler)

