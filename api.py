import requests as requests
from flask import Flask, request, jsonify
from flask_caching import Cache


def pull_rankings():
    rankings = []
    for i in range(10):
        print(f'getting community {i + 1} data...')
        ranking = get_wolves_ranking(i + 1)
        print(ranking)
        rankings.append(ranking)
    rankings = sorted(rankings, key=lambda e: e.__getitem__('attackable_wolves'), reverse=True)
    print(rankings)
    cache.set('rankings', rankings)


config = {
    "DEBUG": False,  # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


def get_wolves(community):
    x = requests.get(f'https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}').json()
    characters = x['characters']
    response = []

    for c in characters:
        c_type = c['type']
        if c_type == 'WOLF':
            wolf = {
                'id': c["id"],
                'alpha': c["traits"]["alpha"],
                'energy': c["energy"],
                'generation': c["generation"],
                'cooldownStartedOn': c["cooldownStartedOn"],
                'cooldownUntil': c["cooldownUntil"]
            }
            response.append(wolf)
    return response


def get_wolves_ranking(community):
    x = requests.get(f'https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{community}').json()
    characters = x['characters']

    wolves = 0
    cooldown_wolves = 0
    for c in characters:
        c_type = c['type']
        if c_type == 'WOLF':
            wolves += 1
            if c["cooldownStartedOn"]:
                cooldown_wolves += 1
    return {
        'cid': community,
        'wolves': wolves,
        'cooldown_wolves': cooldown_wolves,
        'attackable_wolves': wolves - cooldown_wolves
    }


@app.route('/wolves/', methods=['GET'])
def wolves():
    community = request.args.get("c", 1)
    response = get_wolves(community)
    return jsonify(response)


@app.route('/wolves/ranking/', methods=['GET'])
def wolves_ranking():
    rankings = cache.get('rankings')
    # print(f'cached rankings: {rankings}')
    if rankings:
        return jsonify(rankings)
    return []


@app.route('/farmers/', methods=['GET'])
@cache.cached(timeout=600)
def farmers():
    response = []
    for i in range(101):
        x = requests.get(f'https://hdfat7b8eg.execute-api.us-west-2.amazonaws.com/prod/community/{i + 1}').json()
        characters = x['characters']
        print(f'getting community {i + 1} farmers...')
        for c in characters:
            c_type = c['type']
            action = c['action']
            if c_type == "SHEEP" and action:
                a_type = action['type']
                if a_type == 'COLLECTING':
                    data = action['data']
                    farmer_effects = data['farmerEffects']
                    if farmer_effects:
                        for farmer_effect in farmer_effects:
                            farmer = {
                                "id": farmer_effect["farmer"]["id"],
                                "cooldownUntil": farmer_effect["farmer"]["cooldownUntil"]
                            }
                            print(farmer)
                            response.append(farmer)
    return jsonify(response)


@app.route('/')
def index():
    return "<h1>Welcome to our wolf game api!</h1>"


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
