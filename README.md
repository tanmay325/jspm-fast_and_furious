# jspm-fast_and_furious
repository for Library Management system
ReadMe file:
# About the Project
Library Management System Project created with Django. Developed web services using Python (Django Framework).

Objective

Student can
1.	login / signup ,
2.	see their own issues and filter them based on :
-	requested issues ,
-	issued books or
-	all of them together
3.	check their own fine

Admin can

1.	login to admin dashboard
2.	check all issues :
-	see issues ,
-	delete issues ,
-	search issues by studentid
-	filter issues based on :
-	issued or not,
-	returned or not ,
3.	accept a issue :
-	from the dashboard where admin has to manually select return date or
-	from the Issue requests page where return date is automatically calculated
4.	add , delete search books and filter books based on author
5.	add , delete , search author
6.	calculate fine by clicking a button ,
7.	search ,modify,add,delete students , filter them based on department and check all fines and issues of that student

Technologies used:

●	Python
●	Django
●	HTML
●	CSS
●	JS
●	Database: dbSQLite3

Books in homepage will show status of issued , issue requested or request issue based on whether the book is issued or requested for a issue or is not requested for logged-in students only.

-Required to install packages commands
1. pip install django
2. pip install djangorestframework
3. pip install pillow

-Commads to execute project
1. python manage.py makemigrations
2. python manage.py migrate
3. python manage.py runserver
