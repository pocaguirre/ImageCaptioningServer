from flask import Blueprint, jsonify, request, current_app, render_template, make_response
import string
import random
import pandas as pd
import numpy as np
import json

rating = Blueprint('rating', __name__)
# it works, need 400 HITs


def quick_save(worker_id, code, assign_id, answers):
    with open("UserInterface/static/logs.txt", 'a') as f:
        f.write(f"{worker_id}\t{code}\t{assign_id}\t{json.dumps(answers)}\n")


@rating.route('/rating', methods=['GET'])
def get_rating_index():
    sample_ratings = current_app.config['rating_eng'].next()
    sample_ratings = sample_ratings.to_dict(orient='index')
    return render_template("special_rating.html", images=sample_ratings)


@rating.route('/rating_submit', methods=['POST'])
def submit_rating():
    worker_id = request.form['email']
    fname = request.form['first_name']
    lname = request.form['last_name']
    answers = json.loads(request.form['data'])
    current_app.config['rating_eng'].save_answer(worker_id, fname, lname, answers)
    return jsonify({"href": f"/rating_done"})


@rating.route('/rating_done', methods=['GET'])
def done_rating():
    return render_template("rating_ending.html")


@rating.route('/rating_results', methods=['GET'])
def rating_results():
    return current_app.config['rating_eng'].rating_df.to_json(orient='records')


@rating.route('/rating_reset', methods=['GET'])
def rating_reset():
    current_app.config['rating_eng'] = Ratings()
    current_app.logger.info("RESETTING ENGINE")
    return "done"


def id_generator(size=18, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Ratings():
    def __init__(self):
        df = pd.read_csv("all_data.csv")
        df = df[['condition', 'imageset', 'image', 'description']]
        rating_df = pd.concat([df.sample(frac=1).reset_index(), df.sample(frac=1).reset_index()], axis=0, ignore_index=True)
        rating_df['grammar'] = np.nan
        rating_df['correctness'] = np.nan
        rating_df['detail'] = np.nan
        rating_df['email'] = np.nan

        self.rating_df = rating_df
        self.rating_id = 0
        self.max_rating = len(self.rating_df)

    def next(self):
        self.rating_id += 10
        if self.rating_id > self.max_rating:
            self.rating_id = 10
        return self.rating_df[self.rating_id - 10: self.rating_id]

    def save_answer(self, worker_id, fname, lname, answers):
        for key, val in answers.items():
            parts = key.split("_")
            self.rating_df.loc[int(parts[2]), parts[0]] = val
            self.rating_df.loc[int(parts[2]), "email"] = worker_id

    def save(self):
        self.rating_df.to_csv("UserInterface/static/ratings.csv", index=False)
