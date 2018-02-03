# Activate the virtualenv (OS X & Linux)
$ source atf/bin/activate

# Activate the virtualenv (Windows)
$ atf\Scripts\activate

# How to write newly added dependencies to requirements.txt
$ pip freeze > requirements.txt

# How to install dependencies (once inside the venv)
$ pip install -r requirements.txt