import os, pprint, datetime, logging, sys
from todoist_api_python.api import TodoistAPI
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import __main__

pp = pprint.PrettyPrinter(indent=2)

logging.basicConfig(
    level=logging.INFO,
    format="\n[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"./logs/{datetime.datetime.today().strftime('%Y-%m-%d')}_{Path(__main__.__file__).stem}.log",
    filemode='a'
)

if sys.platform == 'darwin':
    token_path = '/Users/tophermckee/todoist_scripts/token.json'
elif sys.platform == 'linux':
    token_path = '/home/tophermckee/todoist_scripts/token.json'

if sys.platform == 'darwin':
    service_account_path = '/Users/tophermckee/todoist_scripts/calendar-api-service-account.json'
elif sys.platform == 'linux':
    service_account_path = '/home/tophermckee/todoist_scripts/calendar-api-service-account.json'


def google_auth_flow():
    SCOPES = [
        "https://www.googleapis.com/auth/calendar"
    ]

    calendar_creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        calendar_creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not calendar_creds or not calendar_creds.valid:
        if calendar_creds and calendar_creds.expired and calendar_creds.refresh_token:
            calendar_creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                service_account_path, SCOPES)
            calendar_creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(calendar_creds.to_json())

    return calendar_creds

if __name__ == '__main__':
    auth_token = os.getenv('TODOIST_AUTH_TOKEN')
    api = TodoistAPI(auth_token)
    
    try:
        calendar_creds = google_auth_flow()
        logging.info('Successfully passed Google Auth Flow')
    except Exception as err:
        logging.error(f"Error in Google Auth Flow: {err}", exc_info=True)

    family_calendar_id = '6d757d0674c5e2f9850aa300bad6aa0bf235fedb5a636aba80474050db297fe5@group.calendar.google.com'
    
    calendar_contents = []

    try:
        page_token = None
        while True:
            service = build('calendar', 'v3', credentials=calendar_creds)
            events = service.events().list(calendarId=family_calendar_id, pageToken=page_token).execute()
            for event in events['items']:
                calendar_contents.append(event['summary'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break
    except Exception as err:
        logging.error(f"Error getting cal events: {err}", exc_info=True)
    
    try:
        all_tasks = api.get_tasks(filter="#🏠 Chores")
        
        for task in all_tasks:
            
            if task.id == '6350698503':
                
                due_date = task.due.date
                litter_due_date = datetime.date(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]))
                scoop_due_date  = datetime.date(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]) - 3)
                scoop_due_datetime  = datetime.datetime(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]) - 3, 20)
                
                if scoop_due_date > datetime.date.today():
                    logging.info(f"{litter_due_date=} {scoop_due_date=}")
                    logging.info('scoop date is in the future')
                    
                    if 'Scoop cat litter' in calendar_contents:
                        logging.info('Scoop cal event already on calendar')
                    else:
                        logging.info('Scoop cal event not on calendar')
                        try:
                            event = {
                                'summary': 'Scoop cat litter',
                                'location': '920 Poeyfarre St Unit 115, New Orleans, LA 70130',
                                'description': 'Courtney so lovingly scoops our sweet babies\'s poo',
                                'start': {
                                    'dateTime': f"{scoop_due_datetime.strftime('%Y-%m-%d')}T20:00:00-06:00",
                                    'timeZone': 'America/Chicago',
                                },
                                'end': {
                                    'dateTime': f"{scoop_due_datetime.strftime('%Y-%m-%d')}T20:30:00-06:00",
                                    'timeZone': 'America/Chicago',
                                },
                                # 'recurrence': [
                                #     'RRULE:FREQ=DAILY;COUNT=2'
                                # ],
                                # 'attendees': [
                                #     {'email': 'lpage@example.com'},
                                #     {'email': 'sbrin@example.com'},
                                # ],
                                'reminders': {
                                    'useDefault': True,
                                    # 'overrides': [
                                    #     {'method': 'email', 'minutes': 24 * 60},
                                    #     {'method': 'popup', 'minutes': 10},
                                    # ],
                                    },
                                }

                            event = service.events().insert(calendarId=family_calendar_id, body=event).execute()
                            
                            logging.info(f"Event created: {event.get('htmlLink')}")

                        except Exception as err:
                            logging.error(f"Error getting cal events: {err}", exc_info=True)

                else:
                    logging.info(f"{litter_due_date=} {scoop_due_date=}")
                    logging.info('scoop date is in the past')

    except Exception as error:
        logging.error(error, exc_info=True) # test for webhook