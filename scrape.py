import requests
from bs4 import BeautifulSoup
import time
import re
from dotenv import load_dotenv
import os
from twilio.rest import Client
import json

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
    #fetch nav 
    soup = BeautifulSoup(page.content, features="html.parser")
    nav = soup.find('nav', class_='pagy-nav')

    hrefs = get_nav_urls(nav)
    soups = []
    pages = [page.text]
  
    for href in hrefs:
        next_page = requests.get(BASE + href)
        soups.append(BeautifulSoup(next_page.content,  features="html.parser"))
        pages.append(next_page.text)
    soups.append(soup)
    
    print("... searched " + str(len(pages)) + " pages")
    for pa in pages:
        matches = re.findall(r"Available Appointments\s*:\s*<\/strong>\s*(\d+)", pa)
        total_appts = sum([int(x) for x in matches])
        if total_appts > 0:
            print("FOUND APPOINTMENTS : " +str(total_appts))
            #notify(vaxsite, "This site has " + str(total_appts) + " appointments! " + url )
            sms("This site has " + str(total_appts) + " appointments! " + url )
            
def walgreens():
    post_content = '{"serviceId":"99","position":{"latitude":42.4326041,"longitude":-71.0557196},"appointmentAvailability":{"startDateTime":"2021-02-26"},"radius":25}'
    post_dict = json.loads(post_content)
    post_response = requests.post("https://www.walgreens.com/hcschedulersvc/svc/v1/immunizationLocations/availability", json=post_dict)
    print(post_response)
    dict_response = post_response.json()
    if dict_response['appointmentsAvailable'] == True:
        sms("Walgreens has slots...!!")
        #notify("Walgreens", "Has slots")

def get_nav_urls(elems):
    ahrefs = elems.find_all('a')
    hrefs = [ ahref['href'] for ahref in ahrefs ]
    return hrefs


if __name__ == "__main__":
    while True:
       # print("Gillette ->> https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=Gillette&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results")
       # get_pages("Gillette","https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=Gillette&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results")
      #  #https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=Fenway&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results
      #  time.sleep(30)
       # print("Fenway ->> https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=Fenway&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results")
      #  get_pages("Fenway", "https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=Fenway&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results")
        walgreens()
        get_pages("ALL", "https://www.maimmunizations.org/clinic/search?location=&search_radius=All&q%5Bvenue_search_name_or_venue_name_i_cont%5D=&q%5Bclinic_date_gteq%5D=&q%5Bvaccinations_name_i_cont%5D=&commit=Search#search_results")
        time.sleep(60)