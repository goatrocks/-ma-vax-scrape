import requests
from bs4 import BeautifulSoup
import time
import re
from dotenv import load_dotenv
import os
from twilio.rest import Client
import json
import datetime

load_dotenv()

def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))
def sms(text):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    from_number = os.environ['FROM_NUMBER']
    to_number = os.environ['TO_NUMBER']
    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body=text,
                     from_=from_number,
                     to=to_number
                 )

BASE = "https://www.maimmunizations.org/"

def get_pages(vaxsite, url):
    #fetch page 
    print("fetching..")
    page = requests.get(url)
    print("got...")
    #main page now prints no more appointments
    if page.text.find("No more appointments") != -1:
        print("...no slots at all...")
        time.sleep(90)
        return
    if page.text.find("Your estimated wait time is") != -1:
        print("...wait list is open...")
        notify("mass vax", "wait list is open for mass vax. Try waiting...")
        time.sleep(90)
        return
    
    #fetch nav 
    soup = BeautifulSoup(page.content, features="html.parser")
    nav = soup.find('nav', class_='pagy-nav')
    if nav is None:
        print("couldn't find the nav...? maybe page error")
        return
    hrefs = get_nav_urls(nav)
    soups = []
    pages = []
  
    for href in hrefs:
        next_page = requests.get(BASE + href)
        soups.append(BeautifulSoup(next_page.content,  features="html.parser"))
        pages.append(next_page.text)
    
    
    print("... searched " + str(len(pages)) + " pages")
    total_appts = 0
    for pa in pages:
        matches = re.findall(r"Available Appointments\s*:\s*<\/strong>\s*(\d+)", pa)
        total_appts += sum([int(x) for x in matches])
    if total_appts > 1:
        print("FOUND APPOINTMENTS : " +str(total_appts))
        #notify(vaxsite, "This site has " + str(total_appts) + " appointments! " + url )
        sms("This site has " + str(total_appts) + " appointments! " + url )
            
def walgreens(client):
    today = datetime.date.today()
    post_content = {
        "serviceId": "99",
        "position": {
            "latitude": 42.4326041,
            "longitude": -71.0557196
        },
        "appointmentAvailability": {
            "startDateTime": today.strftime('%Y-%m-%d')
        },
        "radius": 25
    }
    post_response = client.post("https://www.walgreens.com/hcschedulersvc/svc/v1/immunizationLocations/availability", json=post_content, headers=dict(Referer="https://www.walgreens.com/findcare/vaccination/covid-19/location-screening"))
    if post_response.ok != True:
        print(post_response.status_code)
        if post_response.status_code == 403:
            client = bootstrap_walgreens(requests.Session())
        print("Failed to connect to walgreens....")
        time.sleep(90)
        return
    dict_response = post_response.json()
    if dict_response['appointmentsAvailable'] == True:
        sms("Walgreens has slots...!! https://www.walgreens.com/findcare/vaccination/covid-19/location-screening")
        
    else:
        print("...no slots at walgreens right now...")

def bootstrap_walgreens(client):
    #be polite and get this token...
    resp = client.get("https://www.walgreens.com/browse/v1/csrf")
    csrf = resp.json()
    client.headers.update({csrf['csrfHeaderName']: csrf['csrfToken']})
    return client


def get_nav_urls(elems):
    ahrefs = elems.find_all('a')
    hrefs = [ ahref['href'] for ahref in ahrefs ]
    return hrefs

def cvs(state):
    headers = {"referer": "https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-link2-coronavirus-vaccine"}
    url = f"https://www.cvs.com/immunizations/covid-19-vaccine.vaccine-status.{state}.json?vaccineinfo"
    response = requests.get(url, headers = headers)

    if (response.ok != True):
        print("Failed to connect to CVS....")
        time.sleep(90)
        return
    dict_response = response.json()

    appointments = dict_response['responsePayloadData']['data'][state]
    if (appointments):
        available_appointments = [appointment for appointment in appointments if appointment['status'] != "Fully Booked"]
        if (len(available_appointments) > 0):
            print(available_appointments)
            sms("CVS has" + str(available_appointments) + "slots! https://www.cvs.com/immunizations/covid-19-vaccine")
        else:
            print("No CVS appointments right now")


if __name__ == "__main__":
    while True:
        #get_pages("ALL", "https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=Fenway&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results")
        client = requests.Session()
        client = bootstrap_walgreens(client)
        walgreens(client)
        cvs("MA")
        time.sleep(60)