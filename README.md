# AppTracker

Final project for [CS50 Introduction to Computer Science](https://online-learning.harvard.edu/course/cs50-introduction-computer-science) by Harvard

A Python (Flask) web application that aims to help people keep track of their current and previous job huntings history.

### Technology used: 
- HTML/CSS/JavaScript (Bootstrap, jQuery, Ajax) 
- Python (Flask, Jinja2), SQL (Sqlite3)


## Features

- The user can keep track of each job searches by dividing them in "Projects", displayed on the home page.
- For each projects, there is a dashboard that details the related applications.
- The user can add memo practically everywhere: on projects, on applications, and also on each stages of each applications.
- The main use of this app is to be able to check previous history, so when creating a new application, previously applied companies will be suggested.
There is also a search function for quicker access.


<p align="center">
  <img src="https://raw.githubusercontent.com/ootahiaoo/AppTracker/main/screenshots/1.jpg" width="30%" height="120" title="Home">
  <img src="https://raw.githubusercontent.com/ootahiaoo/AppTracker/main/screenshots/2.jpg" width="30%" height="120" title="Create a new project">
  <img src="https://raw.githubusercontent.com/ootahiaoo/AppTracker/main/screenshots/3.jpg" width="30%" height="120" title="Dashboard">
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/ootahiaoo/AppTracker/main/screenshots/4.jpg" width="30%" height="120" title="Application details">
  <img src="https://raw.githubusercontent.com/ootahiaoo/AppTracker/main/screenshots/5.jpg" width="30%" height="120" title="Add a new application">
  <img src="https://raw.githubusercontent.com/ootahiaoo/AppTracker/main/screenshots/6.jpg" width="30%" height="120" title="Company history">
</p>

## How to use:

Use the `flask run` command inside the `project/application/` folder. If asked, set the path as `export FLASK_APP=application`.

An [online version](https://tahia910.pythonanywhere.com/) is also available.

## Implementation details

The data are stored in a SQLite3 database. I tried to apply the MVC architecture, mainly inspired by [this post](https://www.tutorialspoint.com/python_design_patterns/python_design_patterns_model_view_controller.htm).

`__init__.py` creates and sets up the application, including some custom methods for Jinja2.

`view.py` handles requests from HTML/JavaScript with Jinja2, takes care of displaying information, and also does the back-end's final input validation before sending data to the controller.

`controller.py` stands between `view.py` and `model.py`: it fetches data from `model.py`, handles empty results, transforms the data to another format if necessary, before finally passing the filtered data to `view.py`.

`model.py` focuses on database matters: connecting to the database, making the actual queries, catching database errors and closing the connection. It also includes the object classes that are used to handle the data in `view.py`. I preferred the object way over using dictionnaries as much as possible, because I thought it gave me more control on which data will be passed to the controller/view (and maybe because I am used to this way with Android).

`helpers.py` contains all the miscellaneous short methods that don't apply to any of the files above. It also includes the "fixed" data, such as the error messages or input validation related rules. I kept the error handling method used by Finance CS50, as I thought it looked nice.

Regarding the non-Python files, I separated JavaScript code from HTML, and put all the scripts in three files in the `static/` folder with CSS. I thought it would be more practical than leaving them on HTML files and having to look everywhere when I need to fix something. Doing so allowed me to merge similar scripts as well.

I used an online tool to make the website icon, which automatically gave me all the files in the `static/` folder, except for `pencil.svg`, JavaScript and CSS files.

All the HTML files are in the `templates/` folder. I used Bootstrap on all screens in order to have the app as responsive as possible.
