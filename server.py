from flask import Flask
from flask import request
import requests

app = Flask(__name__)
session_dict = {}

@app.route('/login', methods=['POST', 'GET'])
def login():
    session = requests.Session()

    data = {
        'login': 'EMAIL GOES HERE',
        'password': 'PASSWORD GOES HERE',
        'app': 'plfpl-web',
        'redirect_uri': 'https://fantasy.premierleague.com/a/login'
    }

    request2 = session.post(
        'https://users.premierleague.com/accounts/login/', data=data)

    token = request2.cookies.get('csrftoken')
    session_dict[token] = session
    return token

@app.route('/substitutions', methods=['POST'])
def makeSubstitutes():
    req_data = request.get_json()
    picks = req_data.get('picks')
    token = req_data.get('token')
    session = session_dict[token]

    r = session.post('https://fantasy.premierleague.com/drf/my-team/683158/', json=picks, headers={
        'X-CSRFToken': token,
        'referer': 'https://fantasy.premierleague.com/'
    })

    return r.text
