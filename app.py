import json
import os

import bios
import pandas as pd
import requests
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from werkzeug.utils import secure_filename

config = bios.read("config.yaml")


def allowed_file(filename):
    """Checks if file extension is allowed to

    Args:
        filename (string): Name of the uploaded file to

    Returns:
        bool: True if allowed
    """
    extension = filename.rsplit(".", 1)[1].lower()
    return "." in filename and extension in config["ALLOWED_EXTENSIONS"]


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = config["UPLOAD_FOLDER"]
app.config["SECRET_KEY"] = config["SECRET_KEY"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    """Handles user's uploaded file. Uses request object,
    Checks if file is allowed then store the file in tmp
    and filname in session.
    Calls predict function afterwards

    Returns:
        redirection: Stays on page if no file or file not allowed
        (displays error).
    """
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash(filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            session["current_filename"] = filename
            print(session["current_filename"])
            return redirect(url_for("predict"))
    else:
        flash("NO POST")
        return render_template("index.html", warning="Please select a file")


@app.route("/predict", methods=["GET"])
def predict():
    """Reads user's file and sends it to Azure Web App for
    prediction. Sends back the results to be displayed

    Returns:
        [template]: Displays template with results
    """
    try:
        data = pd.read_csv(
            "{}/{}".format(config["UPLOAD_FOLDER"], session["current_filename"])
        )
        body = json.dumps({"data": data.to_json()})
        res = pd.read_json(requests.post(config["URL"], body, config["HEADERS"]).json())
        return render_template(
            "index.html",
            column_names=res.columns.values,
            row_data=list(res.values.tolist()),
            zip=zip,
        )
    except:
        return "Error handling the file", 400


if __name__ == "__main__":
    app.run()
