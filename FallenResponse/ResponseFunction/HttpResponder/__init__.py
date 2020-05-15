import logging
import smtplib
from email.message import EmailMessage
import azure.functions as func
from azure.cosmos import CosmosClient
from datetime import datetime


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    addr = req.params.get('addr')
    home_id = req.params.get('homeId')
    if not addr and home_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            addr = req_body.get('addr')
            home_id = req_body.get('homeId')

    if addr:
        generate_send_email(addr, home_id)
        return func.HttpResponse(f"Email sent to: {addr}! The database has also logged this entry for home {home_id} at time {datetime.now()}.")
    else:
        return func.HttpResponse(
            "Please pass an email address on the query string or in the request body",
            status_code=400)


def generate_send_email(addr, home_id):
    try:
        home_id = int(home_id)
    except:
        home_id = 5412

    from_addr = "abdevelopertest@gmail.com"
    subj = "CASPAR ALERT: Resident Fallen"
    message = "Warning: A resident has fallen in apartment " + str(home_id)
    smtpserver = 'smtp.gmail.com:587'
    login = "abdevelopertest"
    password = "testaccount123?"  # TODO: Put in environment variables

    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % addr
    header += 'Subject: %s\n' % subj

    message = header + '\n' + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.ehlo()
    server.login(login, password)
    server.sendmail(from_addr, addr, message)
    server.quit()

    # Logging
    database_write(home_id)


def database_write(apt_num):
    db_endpoint = "https://fall-detection-logs.documents.azure.com:443/"
    key = "wNZuwOXUGBnFxbqcEfY1KLIHn7Pq6C1kRG3HhONZydyHaxyPLXBWwyBPK4yQ0HuW545njp84ho300wLsf2BBFA=="
    client = CosmosClient(db_endpoint, {'masterKey': key})
    database_id = "fall-detection-logs1"
    container_id = "logs1-container-1"
    database = client.get_database_client(database_id)
    container = database.get_container_client(container_id)
    now = datetime.now()
    current_time = str(now)
    document = {
        'id': current_time,
        'apartmentNumber': apt_num,
        'time': current_time,
        'description': 'Fallen resident'
    }
    container.create_item(document)
