# jublia-email-endpoint
Interview task - flask POST endpoint

## Endpoint reference:

`/send-emails`
  * POST request
  * expected content type: application/x-www-form-urlencoded
  * Parameters:
    * event_id - integer, must be unique to all other emails
    * email_subject - string
    * email_content - string
    * timestamp - string "YYYY-MM-DD HH:MM:SS" in UTC+8.

The server hosting the application is assumed to run in UTC+8 timezone.
After sending a request to the endpoint, a plain text message should be returned. If saved successfully, a "Successful" message is returned. Otherwise, a 400 bad request is returned, with the error message.

Current error messages implemented:
  * Missing fields: `<, separated list of fields missing>`
  * Bad event\_id (event\_id cannot be converted into integer)
  * Bad timestamp (timestamp in invalid format)
  * Error: `<other reason, usually DB related. e.g. duplicate event_id violates UNIQUE constraint>`

## Setup and Usage

To actually serve the application, a server is required (e.g. apache, nginx). Unfortunately, I don't know how to set up a server yet.

Application:
  * Is python 2 and 3 compatiable
  * Uses cron. Should be run on linux so cron works.
  * Uses sqlite DB.
  * Handles unicode (flask and sqlite will handle unicode by default)
  * Uses custom-made ORM(?) (refer to `database.py` file)

Flask provides a simple development server. You can run this using `start_flask.sh` (linux). For windows, use `start_flask.bat`. (NOTE: cron does not work on windows, so no automated sending.)

A cronjob is used to run `task.py` to send the emails automatically. It searches the database for unsent emails where the timestamp has passed. Use an approporiate SMTP server with login/password. I tried SMTP2go and it works. Currently, it points to mailtrap for development purposes.

Mailtrap inbox link: `https://mailtrap.io/share/246470/5f0e028e2cae139713deb0a22a5c20d9`

`task.py` will output its log into a file called `tasklog.log`. This is simply the event_ids of emails sent. (or any errors if encountered)

Run `makecron.sh` (in this application's directory) to install the cronjob that runs `task.py`. This saves the directory of this application into the cronjob. If the directory is moved, the crontab should be updated manually.

`test.py` is used to send requests to the flask development server. It's *not* a unit test. Results need to be verified manually.

`email-app.py` is the main flask application.

`database.py` is the database script. If changing from sqlite to another database, the new database should be compatible with the exposed interface. Most notably, `Email`, `Recipient`, `DBError` classes, `db_init()` function.

## TODO

In order of priority:
  * Actually serve the application, need to learn how to set up server.
  * Use a taskqueue. (I'm considering zeroMQ. Mostly because want to learn it for other purposes as well.)
  * Use a RDBMS instead of sqlite for better concurrency.
  * Implement an interface to add recipients, instead of in the DB setup.
