HUB DESIGN by Aaron Sun

Hub was an extremely fun project to make and involved many different aspects of programming, working in both the frontend and backend. Over the course of the project, I designed 12 pages in HTML, utilized several hundred lines of CSS, and wrote over 600 lines of code for app.py, cumulatively taking around 30 hours of work. I also gained a lot of experience working with SQL, as it differs heavily from the CS50 IDE. I created Hub using Sublime Text and a MySQL database on my computer, as I wanted to gain more applicable experience (rather than just inside the CS50 IDE). 

Hub was created to be a all-encompassing social network spanning across various social media platforms. Hub was designed to allow people to centrally and easily add each other on various social media platforms, within the social media network of Hub itself. I created Hub using flask, a web framework in Python. Hub is also connected to a working database using mysql.connector. This database was originally hosted locally, edited using MySQLWorkbench. However, I later moved the databases to remotemysql.com, so other people could also utilize the flask app. Hub has various different pathways, many of which pass through @login_required which was used in CS50 finance. Beyond login and register, Hub contains pathways for messaging, posting, friending, viewing profiles, etc. Hub uses a layout.html template that acts as the structure for the rest of the pages. layout.html contains a side-navigation bar that allows for easy website use. Hub's frontend was created completely by me using purely HTML and CSS (except for the dropdown menu under posts, which is cited in the CSS). 

I chose to create Hub because of how decentralized social media was, and wanted to create a network revolving around simplicity and ease-of-access. Hub is simple in terms of design, meant to be easy to use and self-intuitive. While I originally planned on having users only be able to add each other and view their information, I utilized an SQL database to implement various other features. This includes posting and direct messaging. Hub's database uses 6 different tables: users, info, media, friends, posts, and messages. Users stores basic user information, info stores more complicated information, media stores social media information, friends stores friend requests, posts stores global user posts, and messages stores direct messages. These databases are the framework for Hub, which allow users to interact with each other and have individualized experiences, as in any social network. Each user is given an unique id and chooses a unique username, which help organize information between these different tables. Hub also uses session to retain information between requests. Hub also has many features within the HTML and python code to simplify the user experience. HTML input forms are checked within the HTML, and NULL information is also checked within the python code. 
