from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, MTG Collection API!'

if __name__ == '__main__':
    # Runs the app on 0.0.0.0 to be accessible from outside the container
    # and enables debug mode.
    app.run(debug=True, host='0.0.0.0', port=5000)
