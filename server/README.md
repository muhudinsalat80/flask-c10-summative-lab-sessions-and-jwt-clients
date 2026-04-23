# Productivity App Backend

## Install

pip install -r requirements.txt

## Run

flask db upgrade
python app.py

## Routes

POST /signup
POST /login
GET /check_session
DELETE /logout

GET /notes?page=1
POST /notes
PATCH /notes/<id>
DELETE /notes/<id>