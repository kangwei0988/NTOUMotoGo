from .. import app
from flask import redirect,url_for
from .backend import homePage


@app.errorhandler(403) #Forbidden
@app.errorhandler(404) #Not Found
@app.errorhandler(410) #Gone
@app.errorhandler(500) #Internal Server Error
def error_rederict():
    return redirect(url_for('homePage'))
