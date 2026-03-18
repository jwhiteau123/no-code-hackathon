#!/usr/bin/env python3
"""Flask web app for the plant tracker — mobile-friendly browser UI."""

import json
import os
from datetime import date, datetime

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "plants.json")


def load_plants():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_plants(plants):
    with open(DATA_FILE, "w") as f:
        json.dump(plants, f, indent=2)


def days_ago(watered_str):
    try:
        delta = (date.today() - datetime.strptime(watered_str, "%Y-%m-%d").date()).days
        return delta
    except ValueError:
        return None


@app.route("/")
def index():
    plants = load_plants()
    today = date.today().isoformat()
    entries = []
    for entry in sorted(plants.values(), key=lambda p: p["name"].lower()):
        d = days_ago(entry["last_watered"])
        entries.append({
            "key": entry["name"].lower(),
            "name": entry["name"],
            "last_watered": entry["last_watered"],
            "days_ago": d,
            "notes": entry.get("notes", ""),
        })
    return render_template("index.html", plants=entries, today=today)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    watered = request.form.get("watered", "").strip() or date.today().isoformat()
    notes = request.form.get("notes", "").strip()
    if name:
        plants = load_plants()
        key = name.lower()
        if key not in plants:
            plants[key] = {"name": name, "last_watered": watered, "notes": notes}
            save_plants(plants)
    return redirect(url_for("index"))


@app.route("/water/<key>", methods=["POST"])
def water(key):
    watered = request.form.get("watered", "").strip() or date.today().isoformat()
    plants = load_plants()
    if key in plants:
        plants[key]["last_watered"] = watered
        save_plants(plants)
    return redirect(url_for("index"))


@app.route("/note/<key>", methods=["POST"])
def note(key):
    notes = request.form.get("notes", "").strip()
    plants = load_plants()
    if key in plants:
        plants[key]["notes"] = notes
        save_plants(plants)
    return redirect(url_for("index"))


@app.route("/remove/<key>", methods=["POST"])
def remove(key):
    plants = load_plants()
    if key in plants:
        plants.pop(key)
        save_plants(plants)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
