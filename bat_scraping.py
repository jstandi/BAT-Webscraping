from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import time
import json


# function to write data to a json file
def write(json_file, data):
    json.dump(data, open(json_file, 'w'))


# function to retrieve data from a json file
def retrieve(json_file):
    file = open(json_file, 'r')
    data = json.load(file)
    return data


# function to get data from a given auction
elapsed_time = 0


def get_auction_data(link): 
    global elapsed_time
    start_time = time.time()
    # re to capture price
    price_to_int = re.compile('\$(\d*),(\d*)')
    # re to capture year
    date_to_int = re.compile('\d+\/\d+\/(\d\d)')
    # re to capture body type
    title_re = re.compile('(\d{4}).*([Cc]oupe|[Cc]abriolet|[Tt]arga)')
    # re to capture mileage
    mileage_re = re.compile('(\d*)[Kk] Miles')
    # re to capture low mileage
    special_mileage = re.compile('(\d*),(\d*) [Mm]iles')
    # re to capture manual/automatic transmission
    manual_re = re.compile('[Mm]anual [Tt]rans')
    # re to capture year on special types
    special_title_re = re.compile('(\d{4})')
    
    # opens link, parses html response
    response = urlopen(link)
    soup = BeautifulSoup(response)

    try: 
        # finds, captures price sold in html
        price_sold_raw = soup.find('span', class_='info-value noborder-tiny').contents[1].text
        price_match = re.search(price_to_int, price_sold_raw)
        if price_match: 
            price_sold = int(price_match.group(1) + price_match.group(2))
        else: 
            price_sold = None

        # finds, captures year sold in html
        date_sold_raw = soup.find('span', class_='info-value noborder-tiny').contents[3].text
        year_match = re.search(date_to_int, date_sold_raw)
        if year_match: 
            year_sold = int(year_match.group(1))
        else: 
            year_sold = None

        # finds, captures model year, body type in html
        title_raw = soup.find('h1', class_='post-title listing-post-title').contents[0]
        title_match = re.search(title_re, title_raw)
        if title_match: 
            model_year = int(title_match.group(1))
            body_type = title_match.group(2)
        else: 
            model_year = None
            body_type = None

        # finds, captures mileage, manual in html
        details = soup.find_all('div', class_='item')[1].contents[1].contents
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

        # covers edge cases for 'special' types
        special_type = False
        if body_type is None: 
            special_type = True
            special_title_match = re.search(special_title_re, title_raw)
            if special_title_match: 
                model_year = int(special_title_match.group(1))

        # creates list, appends to larger list for csv conversion
        car_data = [price_sold, year_sold, model_year, body_type, manual, mileage, special_type]
        main_data.append(car_data)
    except: 
        print("failed to get data")
    
    end_time = time.time()
    elapsed_time = end_time-start_time
    total_time.append(elapsed_time)
    print("data scraped")
    print(f"time taken: {elapsed_time}s")


# retrieves and stores data from json
retrieved_data = retrieve('bat_data.json')
start_num = retrieved_data['last_viewed']
links = retrieved_data['links']
main_data = retrieved_data['written_data']

total_links = len(links)
total_time = []

# goes through all links and scrapes data, saves if exception
try: 
    for i in range(start_num, total_links): 
        get_auction_data(links[i])
        start_num += 1
        print(f"est. time remaining: {elapsed_time*(total_links-start_num)}s\n{(elapsed_time*(total_links-start_num))/60/60}h")
        print(f"percent complete: {(start_num/total_links)*100}%")

    data_to_write = saved_data_dict = {"last_viewed": start_num, "written_data": main_data, "links": links}
    write('bat_data.json', data_to_write)
    print('done')
except: 
    data_to_write = saved_data_dict = {"last_viewed": start_num, "written_data": main_data, "links": links}
    write('bat_data.json', data_to_write)
    print('an error occured or the program was stopped. data was saved.')
