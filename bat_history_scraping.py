from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import json
  
# need chromedriver for this code to run
# this sets up the chromedriver assuming it is in the root directory
driver = webdriver.Chrome(r"./chromedriver")
options = Options()
options.headless = True
  
# get bat auction results for porsche 911s
driver.get("https://bringatrailer.com/auctions/results/?search=porsche+911")

# xpath for load more button
xpath = "/html/body/main/div[6]/div/div/div/div[2]/div[5]/button"

main_data = [
    ["price_sold", "year_sold", "model_year", "body_type", "is_manual", "mileage", "is_special"]
]

car_num = 0


def write(json_file, data):
    # function to write data to a json file
    json.dump(data, open(json_file, 'w'))
    
    
def retrieve(json_file):
    # function to retrieve data from a json file
    file = open(json_file, 'r')
    data = json.load(file)
    return data


def load_all_auctions(): 
    # function to load all the auctions on bringatrailer.com
    while True: 
        try: 
            # scrolls to bottom of page, click 'load more' button, wait for page to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            button = driver.find_element(By.XPATH, xpath)
            button.click()
            # wait for page to load, depends on connection
            time.sleep(2.5)
        except: 
            break
            
    print("all auctions loaded")


load_all_auctions()

time.sleep(.5)

# gets full html page source
full_page_source = driver.page_source

# closes driver window
driver.quit()

# parses html, finds all auctions
page_soup = BeautifulSoup(full_page_source)
auctions = page_soup.find_all('div', class_='block')

# creates regular expression to filter all auctions that are not cars
filter_ = re.compile('[Ww]heel|[Ff]uch|[Ss]poiler|[Ee]ngine')

auction_links = []
for auction in auctions: 
    # gets the link for each auction from the html data
    link = auction.contents[1].get('href')
    # runs link through re, only adds links that pass filter to list
    filter_match = re.search(filter_, link)
    if not filter_match: 
        auction_links.append(auction.contents[1].get('href'))
        
total_auctions = len(auction_links)
print(total_auctions)

# writes data to json file
saved_data_dict = {"last_viewed": car_num, "written_data": main_data, "links": auction_links}
write('bat_auction_links.json', auction_links)
