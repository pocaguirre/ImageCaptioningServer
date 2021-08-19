from flask import Blueprint, jsonify, request, current_app, render_template, make_response
from flask_cors import CORS, cross_origin
import string
import random
import os.path
import pandas as pd
import numpy as np
import json

rating = Blueprint('rating', __name__)
# cors = CORS(api)


@rating.route('/rating', methods=['GET'])
def get_rating_index():
    return render_template("rating_index.html")


@rating.route('/get_rating', methods=['GET'])
def get_rating():
    worker_id = request.args.get('worker_id', default=None)
    print(f"worker id = {worker_id}")
    global ratings_object
    rating_id = ratings_object.next(worker_id)
    imgs = []
    for i, row in ratings_object.rating_df[ratings_object.rating_df['rating_id'] == rating_id].iterrows():
        imgs.append({'image_url': row['image'], 'description': row['description']})
    resp = make_response(render_template("rating.html", images=imgs))
    resp.set_cookie('worker_id', str(worker_id))
    resp.set_cookie("rating_id", str(rating_id))
    return resp


@rating.route('/rating_submit', methods=['POST'])
def submit_rating():
    global ratings_object
    worker_id = request.form['worker_id']
    rating_id = int(request.form['rating_id'])
    answers = json.loads(request.form['data'])
    assignment = ratings_object.rating_df[ratings_object.rating_df['rating_id'] == rating_id]
    for k, v in answers.items():
        parts = k.split("_")
        ratings_object.rating_df.iloc[assignment.index[int(parts[2]) - 1]][parts[0]].append(v)
    ratings_object.rating_df.loc[assignment.index, 'worker_id'] = assignment.apply(lambda row: row['worker_id'] + [worker_id], axis=1)
    ps = id_generator()
    ratings_object.rating_df.loc[assignment.index, 'assign_ps'] = assignment.apply(lambda row: row['assign_ps'] + [ps], axis=1)

    # TODO: test the MTurk test
    return jsonify({"href": f"/rating_done/{ps}"})


@rating.route('/rating_done/<ps>', methods=['GET'])
def done_rating(ps):
    return render_template("rating_ending.html", survey_code=ps)

def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Ratings():
    def __init__(self):
        rating_id = 0
        if os.path.isfile("ratings.csv"):
            self.rating_df = pd.read_csv("ratings.csv")
        else:
            rating_df = None
            df = pd.read_csv("all_data.csv")
            df = df[['condition', 'imageset', 'image', 'description']]
            for query_string in ["imageset == 'A'", "imageset == 'C'", "imageset == 'B'", "imageset == 'D'"]:
                temp_df = df.query(query_string)
                while len(temp_df) > 0:
                    sampled = temp_df.groupby('image').sample(1, random_state=42)
                    temp_df = temp_df.drop(sampled.index)
                    sampled['rating_id'] = [rating_id for _ in range(len(sampled))]
                    rating_id += 1
                    if rating_df is None:
                        rating_df = sampled
                    else:
                        rating_df = pd.concat([rating_df, sampled], ignore_index=True)
            rating_df['grammar'] = [[] for _ in range(len(rating_df))]
            rating_df['correctness'] = [[] for _ in range(len(rating_df))]
            rating_df['detail'] = [[] for _ in range(len(rating_df))]
            rating_df['worker_id'] = [[] for _ in range(len(rating_df))]
            rating_df['assign_ps'] = [[] for _ in range(len(rating_df))]
            self.rating_df = rating_df
        self.rating_id = 0
        self.max_rating = self.rating_df['rating_id'].max()

    def next(self, worker_id):
        while worker_id in self.rating_df[self.rating_df['rating_id'] == self.rating_id].iloc[0]['worker_id']:
            self.rating_id += 1
            if self.rating_id > self.max_rating:
                self.rating_id = 0
                break
        return self.rating_id


ratings_object = Ratings()
