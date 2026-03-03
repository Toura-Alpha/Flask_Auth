from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if "userneme" in session:
        return redirect(url_for('/dashboard'))
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)