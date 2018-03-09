# Basic test script
import urllib.parse
import urllib.request

data = {"test":"tesy", # extra argument should be ignored.
        "event_id":123,
        "email_subject": "This is a test email.",
        "email_content":"<html><body>this is a test message %amp; Here is a smiley: ☺</body></html>",
        "timestamp":"12-03-2018 00:00:00.000"}

data = urllib.parse.urlencode(data)
data = bytes(data, encoding="utf-8")
req = urllib.request.Request("http://127.0.0.1:5000/save_emails", data=data, method="POST")
with urllib.request.urlopen(req) as f:
    print(f.read())