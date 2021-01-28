# How to run the Forum Flask application

Forum App made with FLASK framework

Installation

```bash
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
```

After this you should open the python3 console and create the database and at the end to exit from the console

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
