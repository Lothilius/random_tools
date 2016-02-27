__author__ = 'Lothilius'

from bottle import Bottle, route, debug, run, template

app = Bottle()

@app.route('/')
def index():
    return template('spark_button')

#add this at the very end:
debug(True)
run(app, host='localhost', port=8080, reloader=True)