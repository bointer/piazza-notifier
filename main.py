from env import Env

from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from piazza_api.rpc import PiazzaRPC
import requests as http
import dateutil.parser
import json
import re
import smtplib

# Set up Piazza connection
piazza = PiazzaRPC(Env.COURSE_NID)
piazza.user_login(Env.PIAZZA_USER, Env.PIAZZA_PASS)

# Set up email connection
if not Env.DEV:
    mailer = smtplib.SMTP('localhost')


def cookie_str(cookie_jar):
    cookies = ['%s=%s' % (name, value) for (name, value) in cookie_jar.items()]
    return ';'.join(cookies)


def get_resources_from_piazza():
    response = http.get(
        Env.RESOURCES_URL,
        headers={
            "Cookie": cookie_str(piazza.session.cookies)
        }
    )
    soup = BeautifulSoup(response.text, features='html.parser')
    script = soup.find_all('script', text=re.compile('RESOURCES'))[0].string
    return json.loads(re.search('var RESOURCES = (.+);', script).group(1))


def get_resource_type(resource):
    rt = resource['config']['section']
    if rt == 'lecture_notes':
        return 'set of lecture notes'
    elif rt == 'homework':
        return 'homework'
    else:
        return 'resource'


def send_email(recipients, subject, body):
    msg = MIMEText(body)
    msg['From'] = f'{Env.SENDER_NAME} <{Env.SENDER_EMAIL}>'
    msg['Subject'] = subject
    mailer.sendmail(Env.SENDER_EMAIL, recipients, msg.as_bytes())


def main():
    print(f'Executing script at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    resources = get_resources_from_piazza()
    last_check_time = datetime.now(timezone.utc) - timedelta(minutes=Env.CHECK_FREQUENCY)

    new_resources = []
    updated_resources = []

    # Build list of new and updated resources
    for resource in resources:
        created = dateutil.parser.parse(resource['created'])
        updated = dateutil.parser.parse(resource['updated'])
        if created > last_check_time:
            new_resources.append(resource)
            continue
        if updated > last_check_time:
            updated_resources.append(resource)

    # Setup database connection
    db = sqlite3.connect(
        Env.DB_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    # Get subscriber list
    # TODO: use firebase
    cur = db.execute('SELECT email, subscribed from emails;')
    records = cur.fetchall()
    cur.close()
    records = filter(lambda record: record['subscribed'] == 1, records)
    subscribers = [record['email'] for record in records]

    emails_sent = 0

    # Send emails
    for resource in new_resources:
        subject = f'New {get_resource_type(resource)} posted for {Env.COURSE_NAME}'
        body = f'A new {get_resource_type(resource)} ({resource["subject"]}) was posted for {Env.COURSE_NAME}.\n' \
               + f'You can view it here: {Env.RESOURCES_URL}.\n\n' \
               + f'You can unsubscribe from this mailing list here: {Env.UNSUBSCRIBE_URL}.'
        if Env.DEV:
            print(subject)
            print(body)
        else:
            send_email(subscribers, subject, body)
            emails_sent += 1

    for resource in updated_resources:
        subject = f'{resource["subject"]} updated for {Env.COURSE_NAME}'
        body = f'{resource["subject"]} was updated for {Env.COURSE_NAME}.' \
               + ' You can view it here: {Env.RESOURCES_URL}.\n\n' \
               + f'You can unsubscribe from this mailing list here: {Env.UNSUBSCRIBE_URL}.'
        if Env.DEV:
            print(subject)
            print(body)
        else:
            send_email(subscribers, subject, body)
            emails_sent += 1

    # Close the database file
    db.close()

    print(f'{len(new_resources)} new resources.')
    print(f'{len(updated_resources)} resources were updated.')
    print(f'{emails_sent} emails sent.')
    print('--- END OF EXECUTION ---\n')


if __name__ == '__main__':
    main()
