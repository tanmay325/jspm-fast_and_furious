from library.forms import IssueBookForm
from django.shortcuts import get_object_or_404, redirect, render,HttpResponse
from .models import *
from django.contrib.auth import authenticate, login, logout
from . import forms, models
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from dal import autocomplete
from .models import IssuedBook, Student, Book

def index(request):
    return render(request, "index.html")

@login_required(login_url='/admin_login')
def add_book(request):
    if request.method == "POST":
        # Extract form data
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']

        if Book.objects.filter(isbn=isbn).exists():
            duplicate_alert = True
            return render(request, "add_book.html", {'duplicate_alert': duplicate_alert})
        else:
            books = Book.objects.create(name=name, author=author, isbn=isbn, category=category)
            books.save()
            success_alert = True
            return render(request, "add_book.html", {'success_alert': success_alert})
    return render(request, "add_book.html")

@login_required(login_url = '/admin_login')
def view_books(request):
    query = request.GET.get('q', '')  # Get the search query from the URL parameters
    books = Book.objects.all()

    if query:
        # Filter books by name, author, or ISBN
        books = books.filter(
            Q(name__icontains=query) | 
            Q(author__icontains=query) | 
            Q(isbn__icontains=query)
        )
    return render(request, "view_books.html", {'books': books, 'query': query})

@login_required(login_url = '/admin_login')
def view_students(request): 
    query = request.GET.get('q', '')  # Get the search query from the URL parameters
    students = Student.objects.all()
    if query:
        # Filter students by name or roll number
        students = students.filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) | 
            Q(roll_no__icontains=query)
        )
    return render(request, "view_students.html", {'students': students, 'query': query})

#new function
@login_required(login_url='/admin_login')
def issue_book(request):
    form = forms.IssueBookForm()
    if request.method == "POST":
        form = forms.IssueBookForm(request.POST)
        if form.is_valid():
            student_id = request.POST['student_name']
            isbn = request.POST['book_isbn']
            
            try:
                book = models.Book.objects.get(isbn=isbn)
            except models.Book.DoesNotExist:
                return render(request, "issue_book.html", {'form': form, 'book_not_available': True})

            if models.IssuedBook.objects.filter(isbn=isbn).exists():
                return render(request, "issue_book.html", {'form': form, 'book_already_issued': True})

            obj = models.IssuedBook()
            obj.student_id = student_id
            obj.isbn = isbn
            obj.save()
            alert = True
            return render(request, "issue_book.html", {'obj': obj, 'alert': alert})

    return render(request, "issue_book.html", {'form': form})


@login_required(login_url='/admin_login')
def view_issued_book(request):  
    issuedBooks = IssuedBook.objects.all()  # Get all issued books  
    details = []
    for i in issuedBooks:
        days = (date.today() - i.issued_date)
        d = days.days
        fine = 0
        if d > 14:
            day = d - 14
            fine = day * 5
        books = list(models.Book.objects.filter(isbn=i.isbn))
        students = list(models.Student.objects.filter(user=i.student_id))
        
        if books and students:
            # Assuming there is exactly one book and one student per issued book.
            book = books[0]
            student = students[0]
            t = (
                student.user, 
                student.user_id, 
                book.name, 
                book.isbn, 
                i.issued_date, 
                i.expiry_date, 
                fine
            )
            details.append(t)
        else:
            # Handle the case where no book or student is found (this should ideally not happen)
            print(f"Warning: No book or student found for issued book with ISBN {i.isbn} and student ID {i.student_id}")
    
    return render(request, "view_issued_book.html", {'issuedBooks': issuedBooks, 'details': details})


@login_required(login_url = '/student_login')
def student_issued_books(request):
    student = Student.objects.filter(user_id=request.user.id)
    issuedBooks = IssuedBook.objects.filter(student_id=student[0].user_id)
    list_of_issued_details = []
    list_of_issued_date = []

    for i in issuedBooks:
        books = Book.objects.filter(isbn=i.isbn)
        for book in books:
            t=(request.user.id, request.user.get_full_name, book.name,book.author)
            list_of_issued_details.append(t)

        days=(date.today()-i.issued_date)
        d=days.days
        fine=0
        if d>15:
            day=d-14
            fine=day*5
        t=(issuedBooks[0].issued_date, issuedBooks[0].expiry_date, fine)
        list_of_issued_date.append(t)
    return render(request,'student_issued_books.html',{'li1':list_of_issued_details, 'li2':list_of_issued_date})

@login_required(login_url = '/student_login')
def profile(request):
    return render(request, "profile.html")

@login_required(login_url = '/student_login')
def edit_profile(request):
    student = Student.objects.get(user=request.user)
    if request.method == "POST":
        student.user.email = request.POST['email']
        student.phone = request.POST['phone']
        student.branch = request.POST['branch']
        student.classroom = request.POST['classroom']
        student.roll_no = request.POST['roll_no']
        student.user.save()
        student.save()
        alert = True
        return render(request, "edit_profile.html", {'alert':alert})
    return render(request, "edit_profile.html")

def delete_book(request, myid):
    books = Book.objects.filter(id=myid)
    books.delete()
    return redirect("/view_books")

def delete_student(request, myid):
    students = Student.objects.filter(id=myid)
    students.delete()
    return redirect("/view_students")

def delete_issue(request, myid, isbn):
    
    try:
        issue = IssuedBook.objects.get(student_id=myid, isbn=isbn)
    except IssuedBook.DoesNotExist:
        return redirect('view_issued_book')
    
    issue.delete()
   
    return redirect('view_issued_book')

def change_password(request):
    if request.method == "POST":
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        try:
            u = User.objects.get(id=request.user.id)
            if u.check_password(current_password):
                u.set_password(new_password)
                u.save()
                alert = True
                return render(request, "change_password.html", {'alert':alert})
            else:
                currpasswrong = True
                return render(request, "change_password.html", {'currpasswrong':currpasswrong})
        except:
            pass
    return render(request, "change_password.html")

def student_registration(request):
    if request.method == "POST":
        Username=request.POST['username']
        password=request.POST['password']
        phone=request.POST['phone']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            passnotmatch = True
            return render(request, "student_registration.html", {'passnotmatch':passnotmatch})

        if User.objects.filter(username=Username).exists():
            return render(request, "student_registration.html", {'username_exists': True})
        
        image = request.FILES['image']
        if image.size > 1024*1024*5:  # 5MB
            return render(request, "student_registration.html",{'image_size':True})
        if not image.name.endswith(('.jpg', '.jpeg', '.png')):
            return render(request, "student_registration.html",{'image_format':True})
       
        user = User.objects.create_user(username=Username, email=request.POST['email'], password=password,first_name=request.POST['first_name'], last_name=request.POST['last_name'])
        student = Student.objects.create(user=user, phone=phone, branch=request.POST['branch'], classroom=request.POST['classroom'],roll_no=request.POST['roll_no'], image=image)
        user.save()
        student.save()
        alert = True
        return render(request, "student_registration.html", {'alert':alert})
    return render(request, "student_registration.html")


def student_login(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return HttpResponse("You are not a student!!")
            else:
                return redirect("/profile")
        else:
            alert = True
            return render(request, "student_login.html", {'alert':alert})
    return render(request, "student_login.html")

def admin_login(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['username'], password=request.POST['password'])

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("/add_book")
            else:
                return HttpResponse("You are not an admin.")
        else:
            alert = True
            return render(request, "admin_login.html", {'alert':alert})
    return render(request, "admin_login.html")

def Logout(request):
    logout(request)
    return redirect ("/")