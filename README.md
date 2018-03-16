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

`task.py` contains the functions to send the emails automatically. Running the script itself will make it send all unsent emails where the timestamp has passed. Use an approporiate SMTP server with login/password. I tried SMTP2go and it works. Currently, it points to mailtrap for development purposes.

Mailtrap inbox link: `https://mailtrap.io/share/246470/5f0e028e2cae139713deb0a22a5c20d9`

`task.py` will output its log into a file called `tasklog.log`. This is simply the event_ids of emails sent. (or any errors if encountered)

Run `makecron.sh` (in this application's directory) to install the cronjob that runs `task.py`. This saves the directory of this application into the cronjob. If the directory is moved, the crontab should be updated manually. *Do not use if using the task queue.*

`test.py` is used to send requests to the flask development server. It's *not* a unit test. Results need to be verified manually.

`email-app.py` is the main flask application.

`database.py` is the database script. If changing from sqlite to another database, the new database should be compatible with the exposed interface. Most notably, `Email`, `Recipient`, `DBError` classes, `db_init()` function.

As a substitute to cron, the application uses a scheduler called rq-scheduler. This uses a Redis backed task queue called rq. (See below)

## Task queue

To setup the task queue, start the programs in the following order:
  1. Redis database
  2. rq worker
  3. rqscheduler
  4. Flask application

rqscheduler was used as what this application requires is not merely a task queue, but a scheduler. rqscheduler provides this functionality.

celery is the most common task queue in python. However, it does not handle scheduled/delayed messages nicely. This is due to the fact that celery stores the entire list of scheduled tasks in its workers. (e.g. https://github.com/celery/celery/issues/2218)

### Redis

From an arbitary directory (probably HOME)

```
wget http://download.redis.io/releases/redis-4.0.8.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-4.0.8
make
make test
```

Use the following to start redis (on default port 6379) in background mode:
`<path to redis folder>/redis-4.0.8/src/redis-server > redis.log 2>&1 &`

Note: Apparently, the & for background mode is not required, redis doesn't get terminated even if it is run in foreground mode and the terminal is killed.

If wanted, install the server using:
`<path to redis folder>/redis-4.0.8/utils/install_server.sh`

This will make redis auto start on boot. Otherwise, redis should be started manually each time if something changes (e.g. computer is rebooted)
Currently, the application uses the queue "default".

### rq-scheduler

Use the following to install rq-scheduler: (https://github.com/rq/rq-scheduler)
`python -m pip install rq-scheduler`

This also automatically installs rq (https://github.com/rq/rq).

In the application directory, use `rq worker > rq_worker.log 2>&1 &` to start the rq worker process. This takes jobs in the redis-based queue and processes them immediately. Starting in the application directory is required for the worker to find the python script of the function to run.

Use `rqscheduler > rq_scheduler.log 2>&1 &` to start the rq-scheduler process. This enqueues jobs in the redis-based queue when the job's scheduled time has been reached.

If any tasks fail, they will be sent to the "failed" queue. They should be manually handled.

If using scheduler, cron job should not be set to prevent double execution of tasks.


## TODO

In order of priority:
  * Actually serve the application, need to learn how to set up server.
  * Use a RDBMS instead of sqlite for better concurrency.
  * Implement an interface to add recipients, instead of in the DB setup.
