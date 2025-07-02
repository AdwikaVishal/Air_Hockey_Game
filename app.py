from flask import Flask, render_template, redirect, url_for
import subprocess
import threading

app = Flask(__name__)

def run_game(script_name):
    subprocess.run(["python3", script_name])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/play/gesture")
def play_with_gesture():
    threading.Thread(target=run_game, args=("gesture_game.py",)).start()
    return redirect(url_for('index'))

@app.route("/play/keyboard")
def play_without_gesture():
    threading.Thread(target=run_game, args=("keyboard_game.py",)).start()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
