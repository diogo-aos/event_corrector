from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time


TOKEN_PATH = 'token.pickle'
APP_CREDENTIALS_PATH = 'credentials_akins_daos.json'
CALENDAR_CONFIG_PATH = 'calendar_tags.pkl'
FETCH_N_EVENTS = 100
ORIGIN_CALENDAR = 'primary'
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']



def get_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                APP_CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def parse_event(title, calendars):
    cals = []
    new_t = title.lower()
    for c_name in calendars.keys():
        c_id = calendars[c_name]['id']
        tags = calendars[c_name]['tags']
        for tag in tags:
            if '#{}'.format(tag.lower()) in new_t:
                return c_id
    return 'primary'

def correct_calendar(calendars, service):
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId=ORIGIN_CALENDAR, timeMin=now,
                                        maxResults=FETCH_N_EVENTS, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        calendar_id = parse_event(event['summary'], calendars)
        if calendar_id == 'primary':
            continue
        service.events().move(calendarId='primary', eventId=event['id'], destination=calendar_id).execute()
        print('changed event {} to calendar {}'.format(event['summary'], calendar_id))

def get_calendar_config(path, service):
    if path is not None and os.path.exists(path):
        with open(path, 'rb') as f:
            calendars = pickle.load(f)
            for c_name in calendars.keys():
                print(c_name, calendars[c_name]['tags'])
            return calendars
    else:
        calendar_list = service.calendarList().list().execute()
        calendars = {}
        for calendar in calendar_list.get('items'):
            calendars[calendar.get('summary')] = {'id': calendar.get('id'), 'tags': []}
            print(calendar.get('summary'))
        
        # specify tags for calendars here
        calendars['CAL']['tags'].extend(['cal'])
        calendars['INT']['tags'].extend(['int', 'internato'])
        calendars['CIAFA']['tags'].extend(['lab', 'ciafa'])
        calendars['Travel']['tags'].extend(['travel', 'trip'])
        calendars['J+D']['tags'].extend(['joana', 'jd'])
        calendars['FAP DS']['tags'].extend(['fap'])
        
        with open(path, 'wb') as f:
            calendars = pickle.dump(calendars, f)
        return calendars

def main():
    print('getting credentials...')
    creds = get_credentials()

    print('getting service...')
    service = build('calendar', 'v3', credentials=creds)

    print('getting calendar tags...')
    calendars = get_calendar_config(CALENDAR_CONFIG_PATH, service)

    print('correcting next {} events...'.format(FETCH_N_EVENTS))
    correct_calendar(calendars, service)


if __name__ == '__main__':
    main()
