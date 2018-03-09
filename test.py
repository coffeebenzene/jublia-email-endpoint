# Basic test script
try: # Python 2
    from urllib2 import Request, urlopen, HTTPError
    from urllib import urlencode
    bytes = lambda x,encoding: x # Replace bytes to do nothing.
except ImportError: # Python 3
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

data = {"test":"tesy", # extra argument should be ignored.
        "event_id":123,
        "email_subject": "This is a test email.",
        "email_content":"<html><body>this is a test message &amp; Here is a smiley: \u263A</body></html>",
        "timestamp":"2018-03-21 00:00:00"}

data = urlencode(data)
data = bytes(data, encoding="utf-8")
req = Request("http://127.0.0.1:5000/save_emails", data=data)
try:
    f = urlopen(req)
    print(f.read())
except HTTPError as e:
    print(e.read())