import os
import requests
import pytz
import datetime
from mastodon import Mastodon

def toot():
    day_format_string = "%Y-%m-%d"
    tz = pytz.timezone("America/Los_Angeles")
    current = datetime.datetime.now(tz=tz)
    current_day = os.getenv('CURRENT_DAY', current.strftime(day_format_string))
    check_time = os.getenv('CHECK_TIME')
    window = int(os.getenv('WINDOW', 10))
    visibility = visibility = os.getenv('VISIBILITY', 'direct')
    schedule = requests.get('https://2018.xoxofest.com/api/events.json')
    events_to_toot = find_events(
        schedule=schedule.json(),
        current_day=current_day,
        check_time=check_time,
        window=window,
    )
    client = Mastodon(
        access_token='de532de78cfa5f758cf00b264468269b836fb4950ab521a09cffa541dfe65fb9',
        api_base_url='https://xoxo.zone',
    )
    for toot in events_to_toot:
        client.status_post(
            status=toot,
            visibility=visibility,
        )

def find_events(schedule, current_day, check_time, window):
    events_to_toot = []
    tz = pytz.timezone("America/Los_Angeles")
    current = datetime.datetime.now(tz=tz)
    if check_time:
        hour, minute = check_time.split(':')
        current = current.replace(hour=8, minute=55)
    for event in schedule:
        if current_day in event['days']:
            current_day_event = event['days'][current_day]
            start_time = datetime.datetime.strptime(current_day_event['start'].upper(), "%I%p")
            start_time = current.replace(hour=start_time.hour, minute=start_time.minute)
            if current < start_time and start_time < (current + datetime.timedelta(minutes=window)):
                toot_string = f"{event['name']} is starting at {current_day_event['start']}!\n\nVenue: {event['venue'].title()}\n\n{current_day_event['description']}"
                if len(toot_string) >= 500:
                    toot_string = toot_string[:490] + '...'
                events_to_toot.append(toot_string)
    return events_to_toot

    
if __name__ == '__main__':
    toot()