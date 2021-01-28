Forum App made with FLASK framework

Installation

''' bash

virtualenv env
source env/bin/activate

pip3 install -r requirements.txt

python3
from main import db
db.create_all()
exit()

export FLASK_APP=main.py
export FLASK_DEBUG=1
export FLASK_ENV=development
flask run
'''
