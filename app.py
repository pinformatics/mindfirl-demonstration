from flask import Flask, render_template, redirect, url_for, session, jsonify, request, g, Response, send_file

import redis
import csv

app = Flask(__name__)

some_condition_for_azure = False
if some_condition_for_azure:
    pass
else:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def process_redis_data(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        original_data = [row for row in reader]

    all_keys = list(r.scan_iter())
    filename_keys = [key for key in all_keys if filename in key]
    filename_values = r.mget(filename_keys)

    first_len = len(filename_values[0].split(','))
    second_len = len(original_data) / 2
    if first_len != second_len:
        raise Exception("The lengths of the dataset {} and responses {} do not line up".format(first_len, second_len))

    html_elements_list = []
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
    
        render_values = [selection_counts[1] + selection_counts[2] + selection_counts[3], selection_counts[4] + selection_counts[5] + selection_counts[6]] + \
            [selection_counts[i] for i in range(1, 7)]

        selection_element = """
            <div>
                <h3 style="white-space: pre;">
                    Different         Same
                    {}                           {}
                </h3>
                <div style="white-space: pre;">
                    H     M     L     L     M     H
                </div>
                <div style="white-space: pre;">
                    {}       {}      {}     {}      {}      {}
                </div>
            </div>
        """.format(*render_values)
        html_elements_list.append(selection_element)

    return original_data, html_elements_list

@app.route('/<filename>')
def display_results_page(filename):
    record_data, selection_html_elements = process_redis_data(filename)
    return render_template("base.html", data=record_data, selections=selection_html_elements)

@app.route('/')
def default_display():
    return display_results_page("data/ppirl.csv")

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

