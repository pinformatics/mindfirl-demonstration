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

    if len(filename_values) != len(data):
        raise Exception("The lengths of the dataset and responses do not line up")

    value_data = [[0] * 7 for _ in range(len(filename_values))]
    for record_index, value in enumerate(filename_values):
        selections = value.split(',')
        for selection_index, selection in enumerate(selections):
            if selection == '':
                value_data[record_index][0] += 1
            else:
                value_data[record_index][int(index)] += 1
    return original_data, value_data

@app.route('/<filename>')
def display_results_page(filename):
    record_data, selection_data = process_redis_data(filename)
    return render_template()

@app.route('/')
def default_display():
    return display_results_page("ppirl.csv")
