from flask import Flask, request, make_response, abort
from redis import Redis
from rq_scheduler import Scheduler
import datetime
import logging

import database
import task

# Setup app
app = Flask(__name__)
app.secret_key = "NUgYcV5U883SS24CBR6kKYa9eQHkD1Sgp7hhwuC51Ok"
app.logger # Initialise the app logger first.
database.db_init()
scheduler = Scheduler(connection=Redis()) # Uses queue "default"

@app.errorhandler(400)
def bad_request(e):
    response = make_response(str(e))
    response.headers["content-type"] = "text/plain"
    response.status_code = 400
    return response

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
    try:
        email = database.Email.create(request_data)
    except database.DBError as e:
        abort(400, "Error: {}".format(e))
    # Schedule email.
    # rq scheduler requires UTC time, but app uses UTC+8, offset.
    scheduler.enqueue_at(email.timestamp - datetime.timedelta(hours=8),
                             task.rq_send_email, email.event_id)
    # Response
    response_str = "Successful"
    response = make_response(response_str)
    response.headers["content-type"] = "text/plain"
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0')
