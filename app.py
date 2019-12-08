# imports necessary libraries
from flask import Flask, request, render_template, redirect, session, flash
from flask_session import Session
from flask_cors import CORS
import os
import mysql.connector
import hashlib
import urllib.parse
from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

app = Flask(__name__)

app.secret_key = os.urandom(24)

# from cs50 finance
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

database = mysql.connector.connect(
		host="localhost",
		user="root",
		passwd="imCaGVRMp13SZcnQ",
		database="cs50db"
	)


db = database.cursor(buffered=True)

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if "user_id" in session:
			return f(*args, **kwargs)
		else:
			return redirect("/login")
	return wrap

@app.route("/")
@login_required
def index():
	id = session["user_id"]
	db.execute("SELECT init FROM users WHERE id = %(id)s", {"id": id})
	infoBool = db.fetchall()
	infoBool = infoBool[0][0]
	if infoBool == 0:
		return redirect("/init")
	else:
		db.execute("SELECT username, posttime, posttext FROM posts WHERE poster_id IN (SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1) OR poster_id IN (SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1) OR poster_id = %(id)s ORDER BY post_id DESC",
					{"id": id})
		feed = db.fetchall()

		return render_template("index.html", feed=feed)

@app.route("/viewprofile")
@login_required
def viewprofile():
	id = session["view_id"]
	db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": id})
	username = db.fetchall()
	username = username[0][0]

	db.execute("SELECT first FROM info WHERE info_id = %(id)s", {"id": id})
	first = db.fetchall()
	if not len(first) == 0:
		first = first[0][0]
	else:
		first = ""

	db.execute("SELECT last FROM info WHERE info_id = %(id)s", {"id": id})
	last = db.fetchall()
	if not len(last) == 0:
		last = last[0][0]
	else:
		last = ""

	db.execute("SELECT bio FROM info WHERE info_id = %(id)s", {"id": id})
	bio = db.fetchall()
	if not len(bio) == 0:
		bio = bio[0][0]
	else:
		bio = "No Biography Yet!"

	db.execute("SELECT * FROM media WHERE media_id = %(id)s", {"id": id})
	media = db.fetchall()
	media = media[0]
	myMedia = []
	print(len(media))
	if not len(media) == 0:
		for i in range(len(media) - 1):
			if media[i] is None:
				if i == 0:
					myMedia.append("No Facebook Information Added.")
				elif i == 1:
					myMedia.append("No Instagram Information Added.")
				elif i == 2:
					myMedia.append("No Twitter Information Added.")
				elif i == 3:
					myMedia.append("No LinkedIn Information Added.")
			else:
				myMedia.append(media[i])

	return render_template("viewprofile.html", username=username, first=first, last=last, bio=bio, media=myMedia)


@app.route("/friends", methods=["GET","POST"])
@login_required
def friends():
	if request.method == "POST":
		id = session["user_id"]

		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1", {"id": id})
		list1 = db.fetchall()

		db.execute("SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1", {"id": id})
		list2 = db.fetchall()

		friendlist = []

		for i in list1:
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		for i in list2:
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		for friend in friendlist:
			db.execute("SELECT id FROM users WHERE username = %(username)s", {"username": friend})
			friend_id = db.fetchall()
			friend_id = friend_id[0][0]

			if request.form.get(friend) == "viewprof":
				session["view_id"] = friend_id
				return redirect("/viewprofile")

			if request.form.get(friend) == "unfriend":
				db.execute("DELETE FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(id)s",
							{"sender": friend_id, "id": id})
				db.execute("DELETE FROM friends WHERE sender_id = %(id)s AND receiver_id = %(receiver)s",
							{"receiver": friend_id, "id": id})
				database.commit()

				message = str(friend) + " has been removed from your friends list"

		flash(message)
		return render_template("friends.html")
	else:
		id = session["user_id"]

		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 1", {"id": id})
		list1 = db.fetchall()

		db.execute("SELECT receiver_id FROM friends WHERE sender_id = %(id)s AND accepted = 1", {"id": id})
		list2 = db.fetchall()

		friendlist = []

		for i in list1:
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		for i in list2:
			friend_id = int(i[0])
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": friend_id})
			friend_user = db.fetchall()
			friend_user = friend_user[0][0]
			friendlist.append(friend_user)

		return render_template("friends.html", friendlist=friendlist)

@app.route("/profile")
@login_required
def profile():
	id = session["user_id"]
	db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": id})
	username = db.fetchall()
	username = username[0][0]

	db.execute("SELECT first FROM info WHERE info_id = %(id)s", {"id": id})
	first = db.fetchall()
	if not len(first) == 0:
		first = first[0][0]
	else:
		first = ""

	db.execute("SELECT last FROM info WHERE info_id = %(id)s", {"id": id})
	last = db.fetchall()
	if not len(last) == 0:
		last = last[0][0]
	else:
		last = ""

	db.execute("SELECT bio FROM info WHERE info_id = %(id)s", {"id": id})
	bio = db.fetchall()
	if not len(bio) == 0:
		bio = bio[0][0]
	else:
		bio = "No Biography Yet!"

	db.execute("SELECT * FROM media WHERE media_id = %(id)s", {"id": id})
	media = db.fetchall()
	media = media[0]
	myMedia = []
	print(len(media))
	if not len(media) == 0:
		for i in range(len(media) - 1):
			if media[i] is None:
				if i == 0:
					myMedia.append("No Facebook Information Added.")
				elif i == 1:
					myMedia.append("No Instagram Information Added.")
				elif i == 2:
					myMedia.append("No Twitter Information Added.")
				elif i == 3:
					myMedia.append("No LinkedIn Information Added.")
			else:
				myMedia.append(media[i])

	return render_template("profile.html", username=username, first=first, last=last, bio=bio, media=myMedia)

@app.route("/edit", methods = ["GET", "POST"])
@login_required
def edit():
	if request.method == "POST":
		id = session["user_id"]
		db.execute("SELECT * FROM users WHERE id = %(id)s", {"id": id})
		rows = db.fetchall()

		if not check_password_hash(rows[0][2], request.form.get("password")):
			flash("Invalid Password.")
			return redirect("/edit")
		else:
			username = request.form.get("username")
			first = request.form.get("first")
			last = request.form.get("last")
			bio = request.form.get("bio")
			fb = request.form.get("fb")
			ig = request.form.get("ig")
			twit = request.form.get("twit")
			link = request.form.get("link")

		db.execute("UPDATE users SET username = %(username)s WHERE id = %(id)s", {"username": username, "id": id})
		db.execute("UPDATE info SET first = %(first)s, last = %(last)s, bio = %(bio)s WHERE info_id = %(id)s", 
						{"first": first, "last": last, "bio": bio, "id": id})
		db.execute("UPDATE media SET fb = %(fb)s, ig = %(ig)s, twit = %(twit)s, link = %(link)s WHERE media_id = %(id)s",
						{"fb": fb, "ig": ig, "twit": twit, "link": link, "id": id})
		database.commit()

		flash("Your profile information has been saved.")
		return redirect("/")
	else:
		id = session["user_id"]
		db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": id})
		username = db.fetchall()
		username = username[0][0]


		db.execute("SELECT first FROM info WHERE info_id = %(id)s", {"id": id})
		first = db.fetchall()
		if not len(first) == 0:
			first = first[0][0]
		else:
			first = ""

		db.execute("SELECT last FROM info WHERE info_id = %(id)s", {"id": id})
		last = db.fetchall()
		if not len(last) == 0:
			last = last[0][0]
		else:
			last = ""

		db.execute("SELECT bio FROM info WHERE info_id = %(id)s", {"id": id})
		bio = db.fetchall()
		if not len(bio) == 0:
			bio = bio[0][0]
		else:
			bio = "No Biography Yet!"

		db.execute("SELECT * FROM media WHERE media_id = %(id)s", {"id": id})
		media = db.fetchall()
		media = media[0]
		myMedia = []
		print(len(media))
		if not len(media) == 0:
			for i in range(len(media) - 1):
				if media[i] is None:
					if i == 0:
						myMedia.append("No Facebook Information Added.")
					elif i == 1:
						myMedia.append("No Instagram Information Added.")
					elif i == 2:
						myMedia.append("No Twitter Information Added.")
					elif i == 3:
						myMedia.append("No LinkedIn Information Added.")
				else:
					myMedia.append(media[i])

		return render_template("edit.html", user=username, first=first, last=last, bio=bio, media=myMedia)

@app.route("/post", methods=["GET","POST"])
@login_required
def post():
	if request.method == "POST":
		my_id = session["user_id"]
		db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": my_id})
		username = db.fetchall()
		username = username[0][0]

		time = datetime.datetime.now()
		text = str(request.form.get("mypost"))
		sendTo = request.form.get("postOptions")
		if sendTo == "all":
			db.execute("INSERT INTO posts (posttext, poster_id, posttime, username) VALUES (%(text)s, %(id)s, %(time)s, %(user)s)", 
						{"text": text, "id": my_id, "time": time, "user": username})
			database.commit()

		flash("Your message has been posted.")

		return render_template("post.html")
	else:
		return render_template("post.html")

@app.route("/add", methods=["GET","POST"])
@login_required
def add():
	if request.method == "POST":
		if request.form.get("button") == "search":
			search = request.form.get("search")
			search = "%" + search + "%"
			db.execute("SELECT username FROM users WHERE LOWER(username) LIKE LOWER(%(search)s)", {"search": search})
			result = db.fetchall()
			resultlist = []
			
			if len(result) == 0:
				flash("Sorry, no results found.")
				return render_template("add.html", resultlist = resultlist)
			else:
				for user in result:
					holder = user[0]
					resultlist.append(holder)
					session["search_list"] = resultlist
				return render_template("add.html", resultlist = resultlist)

		for user in resultlist:
			if request.form.get(str(user)) == "add":
				my_id = session["user_id"]
				result = user
				db.execute("SELECT id FROM users WHERE LOWER(username) = %(result)s", {"result": result})
				request_id = db.fetchall()
				request_id = request_id[0][0]

				if my_id == request_id:
					flash("You can't friend request yourself.")
					return redirect("/add")

				db.execute("SELECT * FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(receiver)s", {"sender": my_id, "receiver": request_id})
				check = db.fetchall()

				db.execute("SELECT * FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(receiver)s", {"sender": request_id, "receiver": my_id})
				check2 = db.fetchall()

				message = ""

				if len(check) == 0 and len(check2) == 0:
					db.execute("INSERT INTO friends (sender_id, receiver_id) VALUES (%(sender)s, %(receiver)s)", {"sender": my_id, "receiver": request_id})
					database.commit()
					message = "A friend request has been sent to " + result
				else:
					if len(check) == 0:
						accepted2 = check2[0][2]
						if accepted2 == 0:
							message = "You already have a request from " + result
						else:
							message = "You are already friends with " + result
					elif len(check2) == 0:
						accepted = check[0][2]
						if accepted == 0:
							message = "A request has already been sent to " + result		
						else:
							message = "You are already friends with " + result	
						
				flash(message)
				return redirect("/add")

			elif request.form.get(str(user)) == "viewprof":
				result = user
				db.execute("SELECT id FROM users WHERE LOWER(username) = %(result)s", {"result": result})
				prof_id = db.fetchall()
				prof_id = prof_id[0][0]
				session["view_id"] = prof_id

				return redirect("/viewprofile")
	else:
		return render_template("add.html")

@app.route("/init", methods=["GET","POST"])
@login_required
def init():
	if request.method == "POST":
		id = session["user_id"]
		first = request.form.get("first")
		last = request.form.get("last")
		bio = request.form.get("bio")

		db.execute("UPDATE info SET first = %(first)s, last = %(last)s, bio = %(bio)s WHERE info_id = %(id)s", 
						{"first": first, "last": last, "bio": bio, "id": id})
		database.commit()

		db.execute("UPDATE users SET init = 1 WHERE id = %(id)s", {"id": id})
		database.commit()

		return redirect("/")
	else:
		return render_template("init.html")

@app.route("/mail", methods=["GET","POST"])
@login_required
def mail():
	if request.method == "POST":
		my_id = session["user_id"]
		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 0", {"id": my_id})
		requestList = db.fetchall()
		myRequests = []

		for requests in requestList:
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": requests[0]})
			holder = db.fetchall()[0]
			myRequests.append(holder)

		message = ""

		for requests in myRequests:
			db.execute("SELECT id FROM users WHERE username = %(username)s", {"username": requests[0]})
			sender_id = db.fetchall()
			sender_id = sender_id[0][0]

			if request.form[str(requests[0])] == "accept":
				db.execute("UPDATE friends SET accepted = 1 WHERE sender_id = %(sender)s AND receiver_id = %(id)s",
							{"sender": sender_id, "id": my_id})
				database.commit()
				message = str(requests[0]) + "'s friend request has been accepted"
			if request.form[str(requests[0])] == "reject":
				db.execute("DELETE FROM friends WHERE sender_id = %(sender)s AND receiver_id = %(id)s",
							{"sender": sender_id, "id": my_id})
				database.commit()
				message = str(requests[0]) + "'s friend request has been rejected"

		flash(message)
		return redirect("/mail")
	else:
		my_id = session["user_id"]
		db.execute("SELECT sender_id FROM friends WHERE receiver_id = %(id)s AND accepted = 0", {"id": my_id})
		requestList = db.fetchall()
		myRequests = []

		for requests in requestList:
			print(requests)
			db.execute("SELECT username FROM users WHERE id = %(id)s", {"id": requests[0]})
			holder = db.fetchall()[0]
			myRequests.append(holder)

		return render_template("mail.html", myList = myRequests)



@app.route("/login", methods=["GET","POST"])
def login():
	if request.method == "POST":
		if request.form["button"] == "register":
			return redirect("/register")
		if request.form["button"] == "login":
			db.execute("SELECT * FROM users WHERE username = %(username)s", {"username": request.form.get("username")})
			rows = db.fetchall()

			if len(rows) == 0:
				flash("Invalid Username.")
				return render_template("login.html")
			if not check_password_hash(rows[0][2], request.form.get("password")):
				flash("Invalid Password.")
				return render_template("login.html")

			session["user_id"] = rows[0][0]

			return redirect("/")
	else:
		return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
	session.clear()
	return redirect("/login")
    
@app.route("/register", methods=["GET","POST"])
def register():
	if request.method == "POST":
		if not request.form.get("password") == request.form.get("confirmation"):
			flash("Your passwords do not match.")
			return render_template("register.html")

		pwHash = generate_password_hash(request.form.get("password"))

		db.execute("SELECT username FROM users WHERE username = %(username)s", {"username": request.form.get("username")})
		userCheck = db.fetchall()
		print(len(userCheck))

		if len(userCheck) == 0:
			newUser = db.execute("INSERT INTO users (username, password) VALUES (%(username)s, %(pw)s)", {'username': request.form.get("username"), "pw": pwHash})
			database.commit()
		else:
			flash("Sorry, that username is already taken.")
			return render_template("register.html")

		db.execute("SELECT * FROM users WHERE username = %(username)s", {"username": request.form.get("username")})
		rows = db.fetchall()

		session["user_id"] = rows[0][0]

		db.execute("INSERT INTO info (info_id) VALUES (%(id)s)", {'id': session["user_id"]})
		database.commit()

		db.execute("INSERT INTO media (media_id) VALUES (%(id)s)", {'id': session["user_id"]})
		database.commit()

		return redirect("/")
	else:
		return render_template("register.html")
