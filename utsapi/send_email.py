from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
 
# create message object instance
msg = MIMEMultipart()

def send_email(subject, message, to):
    
    # setup the parameters of the message
    pwd = "cloud4files.uts"
    msg['From'] = "cloud4files.noreply@gmail.com"
    msg['To'] = to
    msg['Subject'] = subject
    
    # add in the message body
    msg.attach(MIMEText(message, 'plain'))
    
    #create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    
    server.starttls()
    
    server.login(msg['From'], pwd)
    
    
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    
    server.quit()
    
    print("successfully sent email to %s:" % (msg['To']))