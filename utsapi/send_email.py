import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')


path = os.getcwd() +'/utsapi/'

def send_email(subject, url, to, username):
    with open(path +'template_email.html', 'r') as file:
        template = file.read().replace('linkopen', url)
    template = template.replace('username', username)
    
    message = Mail(
        from_email = EMAIL_ADDRESS,
        to_emails = to,
        subject = subject,
        html_content = template)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
    except Exception as e:
        print(e)


# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import smtplib
 
# # create message object instance
# msg = MIMEMultipart()

# def send_email(subject, message, to):
    
#     # setup the parameters of the message
#     pwd = "CLoud42021*"
#     msg['From'] = "cloud4files.noreply@gmail.com"
#     msg['To'] = to
#     msg['Subject'] = subject
    
#     # add in the message body
#     msg.attach(MIMEText(message, 'plain'))
    
#     #create server
#     server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    
    
#     server.starttls()
    
#     server.login(msg['From'], pwd)
    
    
#     # send the message via the server.
#     server.sendmail(msg['From'], msg['To'], msg.as_string())
    
#     server.quit()
    
#     print("successfully sent email to %s:" % (msg['To']))