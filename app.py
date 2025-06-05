from flask import Flask, render_template, redirect, url_for, session, jsonify, request, g, Response, send_file

import redis
import csv

import data_loader as dl
import data_display as dd
import data_model as dm
import os

app = Flask(__name__)

# Initialize Redis connection
redis_url = os.environ.get("REDIS_URL")
if redis_url:
    r = redis.from_url(redis_url)
else:
    # Local development fallback
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", "6379")),
        password=os.environ.get("REDIS_PASSWORD", None),
        ssl=(os.environ.get("REDIS_USE_TLS", "false").lower() == "true"),
        decode_responses=True
    )

# If there are any global variables in the future, initialize them to None here and add 
# @app.before_first_request initialization function

def process_redis_data(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        data_pairs = [row for row in reader]

    all_keys = list(r.scan_iter())
    print(all_keys)
    print(type(all_keys[0]))
    filename_keys = [key for key in all_keys if filename in key]
    filename_values = r.mget(filename_keys)

    num_pairs = len(filename_values[0].split(','))
    data_len = len(data_pairs) / 2
    if num_pairs != data_len:
        raise Exception("The lengths of the dataset {} and responses {} do not line up".format(first_len, second_len))

    html_elements_list = []
    value_data = [[0, 0, 0, 0, 0, 0, 0] for _ in range(num_pairs)]

    for user_index, selection_string in enumerate(filename_values):
        selections = selection_string.split(',')
        for selection_index, selection in enumerate(selections):
            if selection == '':
                value_data[selection_index][0] += 1
            else:
                value_data[selection_index][int(selection)] += 1
    
    print(value_data)

    html_elements_list = []
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

@app.route('/<filename>')
def display_results_page(filename):
    data_pairs, selection_html_elements = process_redis_data(filename)
    
    DATA_PAIR_LIST = dm.DataPairList(data_pairs)
    pairs_formatted = DATA_PAIR_LIST.get_data_display('full')
    title = 'Interactive Record Linkage Results'
    data = list(zip(pairs_formatted[0::2], pairs_formatted[1::2]))
    ids_list = DATA_PAIR_LIST.get_ids()
    icons = DATA_PAIR_LIST.get_icons()[:(len(pairs_formatted) // 2)]
    ids = list(zip(ids_list[0::2], ids_list[1::2]))

    return render_template("base.html", data=data, ids=ids, title=title, icons=icons, selections=selection_html_elements)

@app.route('/')
def default_display():
    return display_results_page("data/ppirl.csv")

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)