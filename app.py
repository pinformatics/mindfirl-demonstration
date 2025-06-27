from flask import Flask, render_template, session, jsonify, request, make_response, Response, url_for
from functools import wraps
from datetime import datetime

import redis
import csv
import pandas as pd
import io

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

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", None)

same_different = {
    "1": "Different",
    "2": "Different",
    "3": "Different",
    "4": "Same",
    "5": "Same",
    "6": "Same"
}

high_low = {
    "1": "High",
    "2": "Moderate",
    "3": "Low",
    "4": "Low",
    "5": "Moderate",
    "6": "High"
}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.form.get('password') != ADMIN_PASSWORD and request.args.get('password') != ADMIN_PASSWORD:
            return "Unauthorized access. Please provide the correct admin password.", 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/admin/download_redis_data', methods=['POST'])
@admin_required
def generate_redis_csv():
    csv_contents = []
    keys = list(r.scan_iter())
    if len(keys) > 0:
        values = r.mget(keys)
        for i, key in enumerate(keys):
            key_data = key.split("file")
            selections = values[i].split(',')
            for record_index, selection in enumerate(selections):
                new_row = [key_data[0], key_data[1], record_index, same_different[selection], high_low[selection]]
                csv_contents.append(new_row)
    
    df = pd.DataFrame(csv_contents, columns=["ID", "File", "Record Index", "Match", "Likelihood"])
    # Convert DataFrame to CSV in-memory
    csv_stream = io.StringIO()
    df.to_csv(csv_stream, index=False)
    csv_stream.seek(0)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Send it as a downloadable response
    return Response(
        csv_stream.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=interactive_record_linkage.csv'}
    )
    
@app.route('/admin/clear_redis', methods=['POST'])
@admin_required
def clear_redis():
    try:
        r.flushall()
        return 'All data cleared from Redis!'
    except redis.ConnectionError as e:
        return "Error clearing Redis: {0}".format(str(e)), 500

@app.route('/admin/view_all_redis_data', methods=['GET'])
@admin_required
def view_all_redis_data():
    try:
        ret = '<h1>All Stored Data in Redis</h1>'
        for key in r.scan_iter("*"):
            user_data = r.get(key)
            # if user_data:
            #     user_data = user_data.decode('utf-8')
            ret += '<strong>{0}:</strong> {1}<br/><br/>'.format(key, user_data)
        return ret
    except redis.ConnectionError as e:
        return "Error connecting to Redis: {0}".format(str(e)), 500
    

def process_redis_data(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data_pairs = [row for row in reader]

    all_keys = list(r.scan_iter())
    print("all keys")
    print(all_keys)
    html_elements_list = []
    value_data = [[0, 0, 0, 0, 0, 0, 0] for _ in range(len(data_pairs))]

    if len(all_keys) > 0:    
        filename_keys = [key for key in all_keys if filename in key]
        filename_values = r.mget(filename_keys)
        if filename_values is None:
            filename_values = []

        num_pairs = len(filename_values[0].split(','))
        data_len = len(data_pairs) / 2
        if num_pairs != data_len:
            raise Exception("The lengths of the dataset and responses are not aligned")

        # html_elements_list = []
        value_data = [[0, 0, 0, 0, 0, 0, 0] for _ in range(num_pairs)]

        for user_index, selection_string in enumerate(filename_values):
            selections = selection_string.split(',')
            for selection_index, selection in enumerate(selections):
                if selection == '':
                    value_data[selection_index][0] += 1
                else:
                    value_data[selection_index][int(selection)] += 1
        

    for selection_counts in value_data:
        render_values = [selection_counts[1] + selection_counts[2] + selection_counts[3], selection_counts[4] + selection_counts[5] + selection_counts[6]] + \
            [selection_counts[i] for i in range(1, 7)]

        selection_element = """
            <div id="overall" 
            style=
            "
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-around;
            margin-top: 4%;
            ">

                <div id="simple-breakdown" style="display: flex; flex-direction: row; justify-content: space-around; align-items: center; font-size: 1.2em; width: 80%">
                    <div id="different-simple" style="flex: 1;">
                        <div>Different</div>
                        <div>{}</div>
                    </div>
                    <div id="same-simple" style="flex: 1">
                        <div>Same</div>
                        <div>{}</div>
                    </div>
                </div>
                <div id="verbose-breakdown" style="display: flex; flex-direction: column; align-items: center; font-size: 0.8em; width: 100%; margin: 2%">
                    <div id="verbose-labels" style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; width: 50%">
                        <span>H</span>
                        <span>M</span>
                        <span>L</span>
                        <span>L</span>
                        <span>M</span>
                        <div>H</div>
                    </div>
                    <div id="verbose-values" style="display: inline-flex; flex-direction: row; justify-content: space-between; width: 50%">
                        <span>{}</span>
                        <span>{}</span>
                        <span>{}</span>
                        <span>{}</span>
                        <span>{}</span>
                        <span>{}</span>
                    </div>
                </div>
            </div>
        """.format(*render_values)

        html_elements_list.append(selection_element)

    return data_pairs, html_elements_list

'''
    for record_index, value in enumerate(filename_values):
        print(value)
        selection_counts = [0] * 7
        selections = value.split(',')
        print(selections)

        for selection_index, selection in enumerate(selections):
            if selection == '':
                selection_counts[0] += 1
            else:
                selection_counts[int(selection)] += 1
    
        
'''

# @app.route('/file/<filename>')
# def display_results_page(filename):
#     try:
#         data_pairs, selection_html_elements = process_redis_data(filename)
        
#         DATA_PAIR_LIST = dm.DataPairList(data_pairs)
#         pairs_formatted = DATA_PAIR_LIST.get_data_display('full')
#         title = 'Interactive Record Linkage Results'
#         data = list(zip(pairs_formatted[0::2], pairs_formatted[1::2]))
#         ids_list = DATA_PAIR_LIST.get_ids()
#         icons = DATA_PAIR_LIST.get_icons()[:(len(pairs_formatted) // 2)]
#         ids = list(zip(ids_list[0::2], ids_list[1::2]))

#         return render_template("base.html", data=data, ids=ids, title=title, icons=icons, selections=selection_html_elements)
#     except Exception as e:
#         return "Can not open invalid or nonexistent file {} {} {}".format(filename, e), 500

# @app.route('/')
# def default_display():
#     return display_results_page("data/ppirl.csv")

# @app.errorhandler(404)
# def page_not_found(e):
#     return "Page not found.", 404

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

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

@app.route('/admin/results')
def results_template():
    filename = "data/ppirl.csv"
    try:
        data_pairs, selection_html_elements = process_redis_data(filename)
        
        DATA_PAIR_LIST = dm.DataPairList(data_pairs)
        pairs_formatted = DATA_PAIR_LIST.get_data_display('full')
        title = 'Interactive Record Linkage Results'
        data = list(zip(pairs_formatted[0::2], pairs_formatted[1::2]))
        ids_list = DATA_PAIR_LIST.get_ids()
        icons = DATA_PAIR_LIST.get_icons()[:(len(pairs_formatted) // 2)]
        ids = list(zip(ids_list[0::2], ids_list[1::2]))

        return render_template("results_base.html", data=data, ids=ids, title=title, icons=icons, results_selections=selection_html_elements)
    except Exception as e:
        return "Can not open invalid or nonexistent file {} {} {}".format(filename, e), 500

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

# @app.route('/<path:invalid_path>')
# def handle_bad_path(invalid_path):
#     return f"'{invalid_path}' doesn't exist.", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)