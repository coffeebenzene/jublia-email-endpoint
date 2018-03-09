from flask import Flask, request, make_response, abort
import database
import logging

# Setup app
app = Flask(__name__)
app.secret_key = "NUgYcV5U883SS24CBR6kKYa9eQHkD1Sgp7hhwuC51Ok"
app.logger # Initialise the app logger first.
database.db_init()

@app.route('/save_emails', methods=["POST"])
def save_emails():
    # Basic validation
    missing = []
    for col in database.Email.columns:
        if col not in request.form:
            missing.append(col)
    if missing:
        missing = ", ".join(missing)
        abort(400, "Bad request: missing fields: {}".format(missing))
    # Save email
    email = database.Email(request.form)
    # TODO
    # Response
    response = make_response("test response\n{}".format(request.form))
    response.headers["content-type"] = "text/plain"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')