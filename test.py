# Basic test script
try: # Python 2
    from urllib2 import Request, urlopen, HTTPError
    from urllib import urlencode
    bytes = lambda x,encoding: x # Replace bytes to do nothing.
except ImportError: # Python 3
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

template_data = {"test":"tesy", # extra argument should be ignored.
                 "event_id":None,
                 "email_subject": "This is test email: ",
                 "email_content":u"<html><body>this is a test message &amp; Here is a smiley: \u263A msg:{} </body></html>",
                 "timestamp":"2018-03-{:02} 00:02:00"}

for i in range(33):
    data = template_data.copy()
    data["event_id"] = i
    data["email_subject"] += str(i)
    data["email_content"] = data["email_content"].format(i)
    data["email_content"] = data["email_content"].encode("utf-8")
    data["timestamp"] = data["timestamp"].format(i)
    
    data = urlencode(data)
    data = bytes(data, encoding="utf-8")
    req = Request("http://127.0.0.1:5000/save_emails", data=data)
    
    print(i)
    try:
        f = urlopen(req)
        print(f.read())
    except HTTPError as e:
        print(e.read())
