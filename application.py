import os
import requests
import json
from helpers import *

from flask import Flask, session,render_template,request,redirect,url_for,Markup
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",methods=["GET","POST"])
@login_required
def index():
    username=session.get('username')
    message=Markup("""<blockquote class="blockquote p-5 mt-5">
    <p>“A reader lives a thousand lives before he dies, said Jojen. <br>The man who never reads lives only one.”</p>
    <footer class="blockquote-footer">George R.R. Martin, A Dance with Dragons </footer>
  </blockquote>""")
    session["books"]=[]   
    if request.method=="POST":
        message=('')
        text=request.form.get('text') 
        data=db.execute("SELECT * FROM books WHERE author iLIKE '%"+text+"%' OR title iLIKE '%"+text+"%' OR isbn iLIKE '%"+text+"%'").fetchall()
        for x in data:
            session['books'].append(x)
        if len(session["books"])==0:
            message=('Nothing found. Try again.')
    return render_template("index.html",data=session['books'],message=message,username=username)

@app.route("/isbn/<string:isbn>",methods=["GET","POST"])
@login_required
def bookpage(isbn):
    warning=""
    username=session.get('username') 
    session["reviews"]=[]
    secondreview=db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND username= :username",{"username":username,"isbn":isbn}).fetchone()
    if request.method=="POST" and secondreview==None:
        review=request.form.get('textarea') 
        rating=request.form.get('stars')
        db.execute("INSERT INTO reviews (isbn, review, rating, username) VALUES (:a,:b,:c,:d)",{"a":isbn,"b":review,"c":rating,"d":username})
        db.commit()
    if request.method=="POST" and secondreview!=None:
        warning="Sorry. You cannot add second review."
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Cdjuz7jTYIwy5Jj9GhY9sw", "isbns": isbn})
    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']
    reviews=db.execute("SELECT * FROM reviews WHERE isbn = :isbn",{"isbn":isbn}).fetchall() 
    for y in reviews:
        session['reviews'].append(y)  
    data=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    return render_template("book.html",data=data,reviews=session['reviews'],average_rating=average_rating,work_ratings_count=work_ratings_count,username=username,warning=warning)

@app.route("/api/<string:isbn>")
@login_required
def api(isbn):
    data=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbn}).fetchone()
    if data==None:
        return render_template('404.html')
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Cdjuz7jTYIwy5Jj9GhY9sw", "isbns": isbn})
    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']
    x = {
    "title": data.title,
    "author": data.author,
    "year": data.year,
    "isbn": isbn,
    "review_count": work_ratings_count,
    "average_score": average_rating
    }
    api=json.dumps(x)
    return render_template("api.json",api=api)

@app.route("/login",methods=["GET","POST"])
def login():
    log_in_message=""    
    if request.method=="POST":
        email=request.form.get('email') 
        userPassword=request.form.get('userPassword')
        emailLogIn=request.form.get('emailLogIn') 
        userPasswordLogIn=request.form.get('userPasswordLogIn')
        if emailLogIn==None:                                  ## registration
            data=db.execute("SELECT username FROM users").fetchall()
            for i in range(len(data)):
                if data[i]["username"]==email:
                    log_in_message="Sorry. Username already exist"
                    return render_template('login.html',log_in_message=log_in_message)
            db.execute("INSERT INTO users (username,password) VALUES (:a,:b)",{"a":email,"b":userPassword})
            db.commit()
            log_in_message="Success! You can log in now."
        else:                                                 ## registration
            data=db.execute("SELECT * FROM users WHERE username = :a",{"a":emailLogIn}).fetchone()
            if data!=None:
                if data.username==emailLogIn and data.password==userPasswordLogIn:
                    session["username"]=emailLogIn
                    return redirect(url_for("index"))
                else:
                    log_in_message="Wrong email or password. Try again."
            else:
                log_in_message="Wrong email or password. Try again."
    return render_template('login.html',log_in_message=log_in_message)
         
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

