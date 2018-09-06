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
    access_token = os.getenv('ACCESS_TOKEN')
    schedule = requests.get('https://2018.xoxofest.com/api/events.json')
    events_to_toot = find_events(
        schedule=schedule.json(),
        current_day=current_day,
        check_time=check_time,
        window=window,
    )
    client = Mastodon(
        access_token=access_token,
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
        current = current.replace(hour=int(hour), minute=int(minute))
    for event in schedule:
        if current_day in event['days']:
            current_day_event = event['days'][current_day]
            events_to_toot.append(
                parse_event(
                    current_day_event,
                    current,
                    window,
                    event['name'],
                    event['venue'],
                    current_day_event.get('start', event.get('start')),
                    '',
                ),
            )
            if event.get('lineup'):
                for lineup_event in event['lineup']:
                    venue = lineup_event.get('location', event.get('venue'))
                    start_time = lineup_event.get('start')
                    if start_time:
                        events_to_toot.append(
                            parse_event(
                                lineup_event,
                                current,
                                window,
                                lineup_event['name'],
                                venue,
                                start_time,
                                '',
                            )
                        )
            if event.get('lineup', [{}])[0].get('subevents'):
                for lineup_event in event['lineup'][0]['subevents']:
                    venue = lineup_event.get('location', event.get('venue'))
                    start_time = lineup_event.get('start', current_day_event.get('start'))
                    events_to_toot.append(
                        parse_event(
                            lineup_event,
                            current,
                            window,
                            lineup_event['name'],
                            venue,
                            start_time,
                            " meetup",
                        )
                    )
    events_to_toot = [toot for toot in events_to_toot if toot is not None]
    return events_to_toot

def parse_event(event, current, window, name, venue, start_time, extra_string=None):
    if ':' in start_time:
        parsed_start_time = datetime.datetime.strptime(start_time.upper(), "%I:%M%p")
    else:
        parsed_start_time = datetime.datetime.strptime(start_time.upper(), "%I%p")
    parsed_start_time = current.replace(
        hour=parsed_start_time.hour,
        minute=parsed_start_time.minute,
    )
    if event.get('location_url'):
        venue = venue + ' ' + event['location_url']
    if current < parsed_start_time and parsed_start_time < (current + datetime.timedelta(minutes=window)):
        toot_string = f"{name}{extra_string} is starting at {start_time}!\n\nVenue: {venue}\n\n{event.get('description', '✨')}"
        if len(toot_string) >= 500:
            toot_string = toot_string[:490] + '...'
        return toot_string

    
if __name__ == '__main__':
    toot()