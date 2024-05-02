import requests
import pytz
from datetime import datetime
from datetime import timedelta
import json

BASE_URL = "https://rest.gohighlevel.com/v1/appointments"
CALENDAR_ID = "WcUIZqqaOUrLtmWIXSM8"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJsb2NhdGlvbl9pZCI6IkkxSjd1QUc4bExPWVJqWjJmbmpGIiwiY29tcGFueV9pZCI6ImJ4RFFzNTBzV0hqeU05akx1cWhLIiwidmVyc2lvbiI6MSwiaWF0IjoxNzAwNTE2MDk0MjExLCJzdWIiOiJ1c2VyX2lkIn0.m0XXMcrSl3m9VsM7A9VO2OZGXjRwKvPCN8olkt5oNmo"
MAX_PER_DAY = 10

def get_auth_headers():
    return {"Authorization": f"Bearer {API_KEY}"}

class SlotAlreadyBookedException(Exception) :    
    pass

def get_availabilities(timezone_p) : 
    now = datetime.now()
    iana_time = pytz.timezone(timezone_p)
    current_time = now.astimezone(iana_time)
    next_time = current_time + timedelta(days=5)
    next_time = next_time.replace(hour=0, minute=0, second=0, microsecond=0)

    start_date = int(current_time.timestamp() * 1000)
    end_date = int(next_time.timestamp() * 1000)

    response = requests.get(
        f"{BASE_URL}/slots?calendarId={CALENDAR_ID}&startDate={start_date}&endDate={end_date}&timezone={timezone_p}",
        headers=get_auth_headers(),
    )

    data = response.json()

    date_list = []
    for date, slots in data.items():
        i = 0
        for slot in slots['slots']:
            if i >= MAX_PER_DAY :
                break
            date_list.append(datetime.fromisoformat(slot))
            i = i + 1
    
    return date_list

def book_appointment(datetime_p, timezone_p):
    try:
        now = datetime.now()
        iana_time = pytz.timezone(timezone_p)
        current_time = now.astimezone(iana_time)
        next_time = current_time + timedelta(days=5)
        next_time = next_time.replace(hour=0, minute=0, second=0, microsecond=0)

        start_date = int(current_time.timestamp() * 1000)
        end_date = int(next_time.timestamp() * 1000)

        datetime_p = datetime_p.astimezone(iana_time)
        
        response = requests.get(
            f"{BASE_URL}/?calendarId={CALENDAR_ID}&startDate={start_date}&endDate={end_date}",
            headers=get_auth_headers(),
        )
        
        data = response.json()

        appointments = data['appointments']
        
        flg = False

        for appointment in appointments:
            if appointment["status"] == 'booked':
                appoint_date = datetime.fromisoformat(appointment["startTime"])
                appoint_date = appoint_date.astimezone(iana_time)
                if datetime_p == appoint_date :
                    flg = True
                    break
        
        if flg :
            raise SlotAlreadyBookedException("Exception: Slot Already Booked")
        else :
            payload = {
                "calendarId": CALENDAR_ID, 
                "selectedSlot": datetime_p.isoformat(),
                "selectedTimezone": timezone_p,
                "email": "test@email.com"
            }

            headers = {}
            headers.update( get_auth_headers() )
            headers.update( { "Content-Type": "application/json" } )

            response = requests.post(BASE_URL, headers=headers, data=json.dumps(payload))

            if response.status_code == 200 :
                print("book successfully")
            else :
                print(response.content, response.status_code)

    except SlotAlreadyBookedException as e:
        print(str(e)) 
        
def main() :

    date_list = get_availabilities("America/New_York")
    
    for date in date_list :
        print(date)

    book_appointment(datetime.fromisoformat("2023-11-25T10:00:00-07:00"), "America/New_York")

if __name__ == "__main__":
    main()
