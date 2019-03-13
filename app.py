from flask import Flask,url_for
app = Flask(__name__)

@app.route('/')
def hello():
    return 'hello'
@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name
@app.route('/test')
def test_url_for():
    return 'qwrqrf'
   
