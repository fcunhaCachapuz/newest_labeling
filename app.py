import os
import shutil
import pandas as pd
from typing import List
from flask import Flask, render_template, request, jsonify

# Visualization
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt

from PIL import Image
from pathlib import Path

import plotly
import kaleido


#from gevent.pywsgi import WSGIServer

app = Flask(__name__)


def weighing_visualization(df: pd.DataFrame) -> List:
    """
    Function to generate weighings plots and save them as images

    Parameters
    ----------
    df : pd.Dataframe
        Pandas Dataframe of file read contents.

    Returns
    -------
    List
        A List of weighings id's.
    """
    df_ids = df.weight_id.unique()
    ids = len(df.weight_id.unique())
    count = 1
    for i in df_ids:
        df_weighingtest = df.loc[df['weight_id'] == i]
        df_weighingtest = df_weighingtest.sort_values(by=['datetime'])
        fig = go.Figure()
        obj = go.Scatter(
        x=df_weighingtest["datetime"], y=df_weighingtest["total_weight"], mode='lines', name="Total")
        fig.add_trace(obj)
        fig.update_layout(
            title={
                'text': i,
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        for j in range(1, 9):
            obj = go.Scatter(
                x=df_weighingtest["datetime"],
                y=df_weighingtest["weight_c{}".format(j)],
                mode='lines', name='LoadCell_{}'.format(j)
            )
            fig.add_trace(obj)
        count = count + 1
        print(i)
        fig.write_image("static/images/{}.png".format(i))
    return df_ids


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        if request.form['submit_button'] == "Load Cells Graphics":
            df = pd.read_csv('static/files/dataset.csv')
            ids = weighing_visualization(df)
            return render_template('index.html')
        elif request.form['submit_button'] == "Weighing Data Labeling":
            imageList = os.listdir('static/images')
            imagelist = [image for image in imageList]
            return render_template("homepage.html", imagelist=imagelist)


@app.route("/index", methods=["GET"])
def index_page():
    return render_template("index.html")


@app.route("/weighinglabeling", methods=["POST"])
def weighinglabeling():
    """
    Labels:
    0 - Normal
    1 - Anomaly
    2 - Not a Weighing
    """
    data = request.json
    weight_id = os.path.splitext(data[1])[0]
    label = int(data[0])

    shutil.move('static/images/{}'.format(data[1]),
                'static/labeling/{}/{}'.format(label, data[1]))

    return f"Weighing with the id: {weight_id} labeled successfully!"


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)