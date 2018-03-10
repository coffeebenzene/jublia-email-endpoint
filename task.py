import database
from email.mime.text import MIMEText
import smtplib
import datetime

# Testing smtp server
smtp_server = "smtp.mailtrap.io"
smtp_user = "c622a5544a57e3"
stmp_pass = "d2750a176d718b"

# Live smtp server.
#smtp_server = "mail.smtp2go.com"
#smtp_user = "jublia-email-endpoint-eric"
#open("smtp2go_pass") as f:
#    stmp_pass = f.read().strip()

application_email = "email_endpoint@example.com"

def send_email(email, recipients):
    subtype = "plain"
    # Crude way to check html email.
    if "<!DOCTYPE html>" in email.email_content or "<html>" in email.email_content:
        subtype = "html"
    msg = MIMEText(email.email_content, subtype, 'utf-8')
    msg["Subject"] = email.email_subject
    msg["From"] = application_email
    msg["To"] = ", ".join(recipients)
    dt = datetime.datetime.now()
    msg["Date"] = dt.strftime("%a, %d %b %Y %H:%M:%S")
    
    client = smtplib.SMTP(smtp_server, 2525)
    client.ehlo()
    client.starttls()
    client.login(smtp_user, stmp_pass)
    client.sendmail(application_email, recipients, msg.as_string())
    client.close()

if __name__ == '__main__':
    emails = database.Email.get_for_send()
    recipients = [e.recipient_email for e in database.Recipient.get_all()]
    for email in emails:
        send_email(email, recipients)
        email.set_sent(True)
        print("sent {}".format(email.event_id))