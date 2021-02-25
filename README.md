Make a .env file with these options to use twilio for your notification

TWILIO_AUTH_TOKEN=
TWILIO_ACCOUNT_SID=
FROM_NUMBER=
TO_NUMBER=

run `pip install -r requirements.txt`

fill in your lattitude and longitude in scrape.py under the walgreens section

mac users: uncomment the notify section for toasts

run `python scrape.py` 

it will send you an sms