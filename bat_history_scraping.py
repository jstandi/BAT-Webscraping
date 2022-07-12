from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import re
import csv
  
# Create the webdriver object. Here the 
# chromedriver is present in the root directory
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
            #scroll to bottom of page, click 'load more' button, wait for page to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            button = driver.find_element_by_xpath(xpath)
            button.click()
            # about 5 second wait for page to load should work, may take longer
            time.sleep(7.5)
        except: 
            break
            
    print("all auctions loaded")
    
def get_auction_data(link): 
    # this function gets data from individual auction pages and is not used in this file
    price_to_int = re.compile('\$(\d*),(\d*)')
    date_to_int = re.compile('\d+\/\d+\/(\d\d)')
    title_re = re.compile('(\d{4}).*([Cc]oupe|[Cc]abriolet|[Tt]arga)')
    mileage_re = re.compile('(\d*)[Kk] Miles')
    special_mileage = re.compile('(\d*),(\d*) [Mm]iles')
    manual_re = re.compile('[Mm]anual [Tt]rans')
    special_title_re = re.compile('(\d{4})')
    response = urlopen(link)
    soup = BeautifulSoup(response)
    
    price_sold_raw = soup.find('span', class_ = 'info-value noborder-tiny').contents[1].text
    price_match = re.search(price_to_int, price_sold_raw)
    if price_match: 
        price_sold = int(price_match.group(1) + price_match.group(2))
    else: 
        price_sold = None
    
    date_sold_raw = soup.find('span', class_ = 'info-value noborder-tiny').contents[3].text
    year_match = re.search(date_to_int, date_sold_raw)
    if year_match: 
        year_sold = int(year_match.group(1))
    else: 
        year_sold = None
    
    title_raw = soup.find('h1', class_ = 'post-title listing-post-title').contents[0]
    title_match = re.search(title_re, title_raw)
    if title_match: 
        model_year = int(title_match.group(1))
        body_type = title_match.group(2)
    else: 
        model_year = None
        body_type = None
    
    details = soup.find_all('div', class_ = 'item')[1].contents[1].contents
    manual = False
    mileage = None
    for detail in details: 
        manual_match = re.search(manual_re, detail.text)
        mileage_match = re.search(mileage_re, detail.text)
        special_mileage_match = re.search(special_mileage, detail.text)
        if manual_match: 
            manual = True
        if mileage_match: 
            raw_mileage = mileage_match.group(1)
            mileage = int(raw_mileage+'000')
        if special_mileage_match: 
            mileage = int(special_mileage_match.group(1) + special_mileage_match.group(2))
    
    special_type = False
    if body_type is None: 
        special_type = True
        special_title_match = re.search(special_title_re, title_raw)
        if special_title_match: 
            model_year = int(special_title_match.group(1))
    
    car_data = [price_sold, year_sold, model_year, body_type, manual, mileage, special_type]
    main_data.append(car_data)
    print("data scraped")
    
def load_auction_data(links): 
    for link in links: 
        get_auction_data(link)
        print(f"{car_num} data sets loaded")
        
load_all_auctions()

time.sleep(.5)

# gets full html page source
full_page_source = driver.page_source

# closes driver window
driver.quit()

# parses html, finds all auctions
page_soup = BeautifulSoup(full_page_source)
auctions = page_soup.find_all('div', class_ = 'block')

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

# old code that would start scraping data instantly
#for num in range(car_num, car_num + 100): 
#    if car_num > total_auctions - 1: 
#        break
#    get_auction_data(auction_links[num])
#    car_num += 1

# writes data to json file
saved_data_dict = {"last_viewed":car_num, "written_data":main_data, "links":auction_links}
write('bat_auction_links.json', auction_links)