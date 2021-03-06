
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_notification_email(to, project, value):
    message = Mail(
        from_email='pamelam@telll.info',
        to_emails=f'{to}',
        subject='BITDROPS Notification',
        html_content=f'<strong>Reminder for {project}. Project {value} in 1 day</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)





