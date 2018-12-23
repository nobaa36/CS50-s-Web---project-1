# Project 1

Web Programming with Python and JavaScript

https://www.youtube.com/watch?v=z3QhACWcvlg

When you start my app first time you will be redirected to login page where you can sign up and log in.
login.html file extends layout.html. Threre are two forms in login page, one for registering a second for logging in.
One and only javascript function check if passwords match durign registration process. Existing users also is checked before registration.
Succesfully registered you can try log in , in case of incorrect data message shows. Once logged in username displays next to log out button.

User is redirected to index.html after logged in. If you requested index by GET , you will see simple quote and will be able search books database. 
If you request index by POST (searching for books) list of books shows. Clicking one of the positions takes you to book.html (bookpage)

book.html file extends layout.html. On bookpage author, year and isbn are loaded. 
Also from goodread.com API rating count and rating itself are loaded. 
Also all reviews received from users along with ratings are loaded one under one. On the bottom there is a plece where you can leave your review
and rating of max 5 points. You can send only one review. On the very bottom there is a link to API page.

Clicking API button you will generate and will be redirected to json file with all data from my application.

Clicking Log out button session is cleared and users is logging out , login.html page is loaded after.

application.py is a main app file. Contains routing to all html files , queries to database and all other functions.
helpers.py contains one function , hecks if there is data in session, if no data found redirect to log in page. 
import.py creates 3 tables-users, reviews and books. After books are created it read csv file and loads all books skipping firs line (title row).  
