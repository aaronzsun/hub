HUB DOCUMENTATION by Aaron Sun

Welcome to Hub! Hub is a fully functioning social network created by Aaron Sun. 

Before Running Hub:
	Hub is flask app in Python. Thus, it requires flask, along with various other Python modules, to successfully run. 
	Make sure you have access to installed all of the following modules before running Hub:

	flask
	flask-session
	os
	mysql.connector
	tempfile
	werkzeug
	datetime

	These modules can also be found at the beginning of app.py, the flask app. You will not be able to run Hub without these modules.

	All of Hub's contents should be found in a folder called cs50_hub. Do not alter the contents of this folder or else the application may not run.
	You should see the following contents within the cs50_hub folder:

	__pycache__
	app.py
	templates
	static
	README.md (this)
	DESIGN.md

	app.py is what runs the flask app. It is commented throughout.
	templates contains the html for Hub's webpages.
	static contains images, JavaScript, and CSS for Hub.
	README.md is Hub's documentation.
	DESIGN.md is Hub's design process. 

Running Hub:
	To run Hub, first open your terminal. CD into the cs50_hub directory. 
	
	IMPORTANT: As of current, the db password is not avaliable to the public.

	Once in the directory, enter "flask_run" (no quotes) into the command line. The terminal should start the server and output various information. You can access Hub through the link provided after "Running on" in the terminal's output.

	You can also access Hub through the link "localhost:5000"

	Now you have Hub running on your own local server! 

How to Use Hub:
	Using Hub is very intuitive. First, you need to register for an account, if you don't already have one. 

	Upon accessing Hub for the first time, you should be on the login page. You can navigate to the register page by clicking "register" or through the "/register" route.

	Here, you will be asked to give a username and password. After successfully registering, you will then be asked for some initial information, including your first name,
	last name, and a short biography. 

	Great! Now you're all set up to use Hub. You should be on a home page that looks relatively empty (since its a new account).

	On the left side of your browser window, you should see 6 icons. From top to bottom, these icons are:

	Hub: Click here to navigate to your home page (your feed).
	Post: Click here to write a post or direct message.
	Profile: Click here to view and edit your profile.
	Friends List: Click here to manage your friends list and view your friend's profiles.
	Add Friends/Search: Click here to search for users to add or to view their profiles.
	Mail: Click here to view your friend requests and direct messages.

	More in-depth information:
		Hub: This is where you can see all your friend's posts. It will display these posts with the most recent ones at the top, and the oldest ones at the bottom. These posts will contain a username, a timestamp, and a message.

		Post: This is where you can make a post or direct message. In the text area type a post (limited to 500 chars), and then use the dropdown menu to choose where to send your post. In the dropdown menu, you should see "All Friends" and the usernames of your friends. Select "All Friends" to send your post to everyone (visible in the Hub), or choose a specific friend to make a direct message. This message will show up in their inbox.

		Profile: This is where you can view your profile. It will show your name, picture (not implemented yet), your biography, and your social media information. It will be preset to "No Information Added." You can add this information and edit the rest of your profile by clicking "Edit Profile" at the bottom of your profile box. This will redirect you to "/edit" where you can make changes to your profile, confirming your identity by entering your password at the bottom. The input boxes should be autofilled to your current information, which you can edit at your discretion. 

		Friends List: This is where you can view your list of friends. Each friend should have two options below their usename: "View Profile" and "Unfriend". "View Profile" will take you to their profile page. "Unfriend" will remove them from your friend list.

		Add Friends/Search: Here, you can look up other users. Type a search entry into the search box and click search. This will return any usernames containing your inputed string. These results will display below the search box. For each result, you will have the option to "View Profile" or "Add". "View Profile" will show you their profile. "Add" will send them a friend request, unless you are already friends or have already sent/received a request.

		Mail: This is where you can respond to friend requests and see your direct messages. Respond to a friend request by either clicking "Accept" or "Reject" under the requester's username. Underneath these requests, you will see any direct messages sent to you. These will be formated the same as posts.

	While I can't control the uptime of the SQL database, restarting the Hub upon encountering database connection errors usually solves the issue.

How to Stop Hub:
	To stop the Hub flask app from running, go to your terminal and hit "Ctrl + C".


Thanks for using Hub!





