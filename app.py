from flask import Flask, render_template, session, jsonify, request, make_response

import redis
import csv

import data_loader as dl
import data_display as dd
import data_model as dm
import os
import uuid

app = Flask(__name__)

# Initialize Redis connection
redis_url = os.environ.get("REDIS_URL")
if redis_url:
    r = redis.Redis(
        host='mindfirl-redis.redis.cache.windows.net',    
        port=6380,                  
        username='default',         
        password=os.environ.get("REDIS_PASSWORD", None),
        ssl=True,                  
        decode_responses=True
    )
else:
    # Local development fallback
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        password=os.environ.get("REDIS_PASSWORD", None),
        ssl=(os.environ.get("REDIS_USE_TLS", "false").lower() == "true"),
        decode_responses=True
    )

# Global variables
data_path = 'data/ppirl.csv'
DATASET = None
data_pairs = None
DATA_PAIR_LIST = None
flag = False
user_selections = None

@app.route('/<filename>')
def display_results_page(filename, template_name):
    global user_selections
    
    user_id = request.cookies.get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())

    try:
        with open(filename, newline='') as f:
            reader = csv.reader(f)
            data_pairs = [row for row in reader]
        
        DATA_PAIR_LIST = dm.DataPairList(data_pairs)
        pairs_formatted = DATA_PAIR_LIST.get_data_display('full')
        title = 'Interactive Record Linkage'
        data = list(zip(pairs_formatted[0::2], pairs_formatted[1::2]))
        ids_list = DATA_PAIR_LIST.get_ids()
        icons = DATA_PAIR_LIST.get_icons()[:(len(pairs_formatted) // 2)]
        user_selections = [""] * (len(pairs_formatted) // 2)
        ids = list(zip(ids_list[0::2], ids_list[1::2]))
    except Exception as e:
        return "Can not open invalid or nonexistent file {} {} {}".format(filename, e, os.getcwd()), 500
    
    response = make_response(render_template(template_name, data=data, ids=ids, title=title, icons=icons))
    response.set_cookie("user_id", user_id)
    return response

def default_display(screen_width):
    return display_results_page("data/ppirl.csv", screen_width)

@app.route('/')
def index():
    # Just serves the base page with JavaScript
    return render_template('landing.html')

@app.route('/desktop')
def desktop():
    return display_results_page("data/ppirl.csv", "base.html")

@app.route('/mobile')
def mobile():
    return display_results_page("data/ppirl.csv", "mobile.html")

@app.route('/update_selection', methods=['POST'])
def update_selection():
    global user_selections
    data = request.get_json()
    button_id = data['id']
    index = int(button_id[1:2])
    selection = button_id[3:]
    user_selections[index] = selection
    return jsonify(success=True)

@app.route('/submit_selections', methods=['POST'])
def submit_selections():
    global user_selections
    user_id = request.cookies.get("user_id")
    if not user_id:
        # return jsonify(success=False, error="No User ID"), 400
        user_id = "no_user_id"
    
    r.set("id:" + user_id + "___file:" + data_path, ','.join(user_selections))
    return jsonify(success=True)

# @app.route('/screen', methods=['POST'])
# def screen():
#     screen_width = request.json.get('width')

#     # Decide based on width
#     return jsonify({'template': default_display(screen_width)})
#     # return jsonify({'template': render_template('mobile.html')})

@app.route('/<path:invalid_path>')
def handle_bad_path(invalid_path):
    return f"'{invalid_path}' doesn't exist.", 404

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)