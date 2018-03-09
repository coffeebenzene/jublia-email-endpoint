from flask import Flask, request, make_response, abort
import datetime
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
    for field in database.Email.accepted_input:
        if field not in request.form:
            missing.append(field)
    if missing:
        missing = ", ".join(missing)
        abort(400, "Missing fields: {}".format(missing))
    request_data = request.form.to_dict()
    try:
        request_data["event_id"] = int(request_data["event_id"])
    except ValueError:
        abort(400, "Bad event_id")
    try:
        request_data["timestamp"] = datetime.datetime.strptime(request_data["timestamp"],
                                                               "%Y-%m-%d %H:%M:%S")
    except ValueError:
        abort(400, "Bad timestamp")
    
    # Save email
    email = database.Email(request_data)
    # TODO
    # Response
    response = make_response("test response\n{}".format(request.form))
    response.headers["content-type"] = "text/plain"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')