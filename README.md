Pre-reqs: This is python3, specifically tested with python 3.8 on mac. It definitely won't work with python 2. I use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) for managing python environments.

Steps:

Make a .env file with these options to use twilio for your notification

TWILIO_AUTH_TOKEN=

TWILIO_ACCOUNT_SID=

FROM_NUMBER=

TO_NUMBER=

Once that file is set...

run `pip install -r requirements.txt`

fill in your lattitude and longitude in scrape.py under the json for the walgreens section 

At the bottom of the file, you can uncomment/comment out the providers you want to see

```
 #get_pages("ALL", "https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=Fenway&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results")
        client = requests.Session()
        client = bootstrap_walgreens(client)
        walgreens(client)
        cvs("MA")
        time.sleep(60)


```

mac users: uncomment the notify section for toasts



run `python scrape.py` 

it will send you an sms if it finds any slots. be fast, have your info saved in autofill using one of those advanced autofill plugins


This is a little rough n tumble but hopefully it helps you!


