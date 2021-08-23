from flask import Blueprint, jsonify, request, current_app, render_template, make_response
import string
import random
import pandas as pd
import numpy as np
import json

rating = Blueprint('rating', __name__)
# it works, need 400 HITs


@rating.route('/rating', methods=['GET'])
def get_rating_index():
    return render_template("rating_index.html")


@rating.route('/get_rating', methods=['GET'])
def get_rating():
    worker_id = request.args.get('worker_id', default=None)
    current_app.logger.info(f"worker id = {worker_id}")
    rating_id = current_app.config['rating_eng'].next(worker_id)
    imgs = []
    for i, row in current_app.config['rating_eng'].rating_df[current_app.config['rating_eng'].rating_df['rating_id'] == rating_id].iterrows():
        imgs.append({'image_url': row['image'], 'description': row['description']})
    resp = make_response(render_template("rating.html", images=imgs))
    resp.set_cookie('worker_id', str(worker_id))
    resp.set_cookie("rating_id", str(rating_id))
    return resp


@rating.route('/rating_submit', methods=['POST'])
def submit_rating():
    worker_id = request.form['worker_id']
    rating_id = int(request.form['rating_id'])
    answers = json.loads(request.form['data'])
    assignment = current_app.config['rating_eng'].rating_df[current_app.config['rating_eng'].rating_df['rating_id'] == rating_id]
    for k, v in answers.items():
        parts = k.split("_")
        current_app.config['rating_eng'].rating_df.iloc[assignment.index[int(parts[2]) - 1]][parts[0]].append(v)
    current_app.config['rating_eng'].rating_df.loc[assignment.index, 'worker_id'] = assignment.apply(lambda row: row['worker_id'] + [worker_id], axis=1)
    ps = id_generator()
    current_app.config['rating_eng'].rating_df.loc[assignment.index, 'assign_ps'] = assignment.apply(lambda row: row['assign_ps'] + [ps], axis=1)
    current_app.config['rating_eng'].save()
    return jsonify({"href": f"/rating_done/{ps}"})


@rating.route('/rating_done/<ps>', methods=['GET'])
def done_rating(ps):
    return render_template("rating_ending.html", survey_code=ps)


@rating.route('/rating_results', methods=['GET'])
def rating_results():
    return current_app.config['rating_eng'].rating_df.to_json(orient='records')


@rating.route('/rating_reset', methods=['GET'])
def rating_reset():
    current_app.config['rating_eng'] = Ratings()
    current_app.logger.info("RESETTING ENGINE")
    return "done"


def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Ratings():
    def __init__(self):
        rating_id = 0
        rating_df = None
        df = pd.read_csv("all_data.csv")
        df = df[['condition', 'imageset', 'image', 'description']]

        while len(df) > 0:
            for query_string in ["imageset == 'A'", "imageset == 'C'", "imageset == 'B'", "imageset == 'D'"]:
                temp_df = df.query(query_string)
                if len(temp_df) > 0:
                    sampled = temp_df.groupby('image').sample(1, random_state=42)
                    df = df.drop(sampled.index)
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
        self.rating_id = -1
        self.max_rating = self.rating_df['rating_id'].max()
        self.max_number_raters = 3

    def next(self, worker_id):
        self.rating_id += 1
        if self.rating_id > self.max_rating:
            self.rating_id = 0
        while (worker_id in self.rating_df[self.rating_df['rating_id'] == self.rating_id].iloc[0]['worker_id']) or\
            (len(self.rating_df[self.rating_df['rating_id'] == self.rating_id].iloc[0]['worker_id']) > 2):
            self.rating_id += 1
            if self.rating_id > self.max_rating:
                self.rating_id = 0
                break
        return self.rating_id

    def save(self):
        self.rating_df.to_csv("ratings.csv", index=False)
