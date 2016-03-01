__author__ = 'Lothilius'

from bottle import Bottle, route, debug, run, template

app = Bottle()

@app.route('/')
def index():
    environment=''
    return template('live_chat_button', environment=environment)


@app.route('/<environment>')
def other(environment=''):
    return template('live_chat_button', environment=environment)

@app.error(404)
def error404(error):
    return 'Nothing here, sorry'

#add this at the very end:
debug(True)
run(app, host='localhost', port=8080, reloader=True)