from flask import Flask
from flask import request
from flask import jsonify, make_response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
session_dict = {}

@app.route('/login', methods=['POST'])
def login():
    print("logging in")
    session = requests.Session()
    username = request.get_json().get("username")
    password = request.get_json().get("password")

    request1 = session.post('https://fantasy.premierleague.com/')
    data = {
        'login': username,
        'password': password,
        'app': 'plfpl-web',
        'redirect_uri': 'https://fantasy.premierleague.com/'
    }
    request2 = session.post(
        'https://users.premierleague.com/accounts/login/', data=data)

    token = session.cookies.get('csrftoken')
    session_dict[token] = session
    return jsonify({
        "token": token
    })

@app.route("/me", methods=['GET', 'POST'])
def getInfo():
    req_data = request.get_json()
    token = req_data.get('token')
    session = session_dict[token]

    res = session.get('https://fantasy.premierleague.com/api/me/', headers={
        'X-CSRFToken': token,
        'referer': 'https://fantasy.premierleague.com/'
    })

    player = res.json()['player']
    extra_info_url = 'https://fantasy.premierleague.com/api/entry/' + str(player['entry'])

    morePlayerInfo = session.get(extra_info_url, headers={
        'X-CSRFToken': token,
        'referer': 'https://fantasy.premierleague.com/'
    }).json()

    team_info_url = 'https://fantasy.premierleague.com/api/my-team/' + str(player['entry'])
    teamRes = session.get(team_info_url, headers={
        'X-CSRFToken': token,
        'referer': 'https://fantasy.premierleague.com/'
    }).json()



    return jsonify({
        "player": {
            'id': player['entry'],
            'name': player['first_name'] + " " + player['last_name'],
            'country': morePlayerInfo['player_region_iso_code_short'],
            'team_name': morePlayerInfo['name'],
            'leagues': morePlayerInfo['leagues']['classic'],
            'picks': teamRes['picks']
        }
    })

@app.route("/static", methods=['GET', 'POST'])
def getStaticData():
    req_data = request.get_json()
    token = req_data.get('token')
    session = session_dict[token]

    res = session.get('https://fantasy.premierleague.com/api/bootstrap-static/', headers={
        'X-CSRFToken': token,
        'referer': 'https://fantasy.premierleague.com/'
    }).json()

    return jsonify({
        'players': res['elements'],
        'teams': res['teams']
    })

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
