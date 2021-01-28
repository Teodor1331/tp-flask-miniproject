# How to run the Forum Flask application

Forum App made with FLASK framework

The webserver was made on Ubuntu 18.04 and on Windows Operational System this guide will be definitely useless,
because there you should have many other things installed on your computer first and the commands are different.

For the application we will need virtualenv environment installed, if you don't install it with:

```bash
pip3 install virtualenv 
```

Installation (it is supposed you are in your user folder, otherise, first navigate to the project folder and just pass the first command from below. The folder by default is called tp-flask-miniproject, but downloading the code
will show it as tp-flask-miniproject-master after unzipping the archive with the project):

```bash
cd tp-flask-miniproject-master/
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```

After this you should open the python3 console and create the database and at the end to exit from the console:

```bash
python3
from main import db
db.create_all()
exit()
```

Then you should start the application with these commands:

```bash
export FLASK_APP=main.py
export FLASK_DEBUG=1
export FLASK_ENV=development
flask run
```
