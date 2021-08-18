from flask import Blueprint, jsonify, request, current_app, render_template
from flask_cors import CORS, cross_origin
import string
import random
import os.path
import pandas as pd
import numpy as np

rating = Blueprint('rating', __name__)
# cors = CORS(api)
rating_df = None


@rating.route('/rating', methods=['GET'])
def get_rating_index():
    return render_template("rating_index.html")


@rating.route('/get_rating', methods=['GET'])
def get_rating():
    worker_id = request.args.get('worker_id', default=None)
    print(f"worker id = {worker_id}")
    global rating_df
    rating_id = np.random.randint(0, rating_df['rating_id'].max())
    while worker_id not in rating_df[rating_df['rating_id'] == rating_id].loc[0, 'worker_id']:
        rating_id = np.random.randint(0, rating_df['rating_id'].max())
    imgs = []
    for i, row in rating_df[rating_df['rating_id'] == rating_id]:
        imgs.append({'image_url': row['image'], 'description': row['description']})
    return render_template("rating.html", images=imgs)


def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def set_up():
    global rating_df
    rating_id = 0
    if os.path.isfile("ratings.csv"):
        rating_df = pd.read_csv("ratings.csv")
    else:
        df = pd.read_csv("all_data.csv")
        df = df[['condition', 'imageset', 'image', 'description']]
        for query_string in ["imageset == 'A' or imageset == 'C'", "imageset == 'B' or imageset == 'D'"]:
            temp_df = df.query(query_string)
            while len(temp_df) > 0:
                sampled = temp_df.groupby('image').sample(1, random_state=42)
                temp_df = temp_df.drop(sampled.index)
                sampled['rating_id'] = rating_id
                rating_id += 1
                if rating_df is None:
                    rating_df = sampled
                else:
                    rating_df = pd.concat([rating_df, sampled], ignore_index=True)
        rating_df['grammar'] = [[] for _ in range(len(rating_df))]
        rating_df['correctness'] = [[] for _ in range(len(rating_df))]
        rating_df['detail'] = [[] for _ in range(len(rating_df))]
        rating_df['worker_id'] = [[] for _ in range(len(rating_df))]


def is_new_worker(worker_id):
    global rating_df
    if rating_df is None:
        return True
    for i, r in rating_df.iterrows():
        if worker_id in r['worker_id']:
            return False
    return True

