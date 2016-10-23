from selenium import webdriver 
import csv
import time 
import pymssql


proxies_list = ['addr1:port1', 'addr2:port2']
db = pymssql.connect("localhost", "test", "test", "testdb")

cursor = db.cursor()

browser = webdriver.Chrome(executable_path='C:\Users\Administrator\Downloads\chromedriver_win32\chromedriver.exe')

csvwriter = csv.writer(file('final.csv', 'wb'))
#csvwriter.writerow(['Street', 'City', 'Region', 'Postal', 'Product Name', 'Price', 'Beds', 'Baths', 'Square Feet', 'Lot Size', 'Property Type', 'Broker'])

def write_to_log(msg):
    '''
    Appends error/success message to log file error_log.txt in the current directory.
    '''
    with open("error_log.txt", "ab") as f:
        f.write(msg)

def get_property_from_db(address):
    cursor.execute('SELECT * FROM listing WHERE addr = %s', address)
    results = cursor.fetchall()
    if len(results) > 0:
        return True

    return False


def insert_property(property_details):
    '''
    Inserts property to database
    '''
    property_details = [each_p.encode('utf-8') for each_p in property_details]
    csvwriter.writerow(property_details)
    
    try:
        cursor.execute("INSERT INTO listing VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (property_details[0], property_details[1],property_details[2],property_details[3],property_details[4],property_details[5],property_details[6],property_details[7],property_details[8],property_details[9],property_details[10],property_details[11],property_details[12],property_details[13],property_details[14],property_details[15],property_details[16],property_details[17],property_details[18],property_details[19]))
        db.commit()
    except:
        msg = "insert property " + msid + " Could not insert property to db."
        write_to_log(msg)
        print "couldn't insert"
        db.rollback()



def get_essential_info(all_individual_contents):
    to_visit_link = []
    to_visit_street = []
    to_visit_city = []
    to_visit_region = []
    to_visit_postal = []
    to_visit_price = []
    for each_content in all_individual_contents:
        try:
            photo_label = each_content.find_element_by_class_name("srp-item-photo-label")
            photo_label_content = photo_label.find_element_by_tag_name("span")
            label = photo_label_content.text
        except:
            continue
        if label != "New":
            continue
        try:
            street = each_content.find_element_by_class_name("listing-street-address").text
        except:
            street = ""
        if street != "":
            if get_property_from_db(street):
                continue
        to_visit_street.append(street)
        li_for_link = each_content.find_element_by_class_name("srp-item-address")
        each_link = li_for_link.find_element_by_tag_name("a")
        each_link = each_link.get_attribute("href")
        to_visit_link.append(each_link)
        try:
            city = each_content.find_element_by_class_name("listing-city").text
        except:
            city = ""

        try:
            region = each_content.find_element_by_class_name("listing-region").text
        except: 
            region = ""
        try: 
            postal = each_content.find_element_by_class_name("listing-postal").text
        except:
            postal = ""
        try:  
            price = each_content.find_element_by_class_name("srp-item-price").text
        except:
            price = ""
        to_visit_city.append(city)
        to_visit_region.append(region)
        to_visit_postal.append(postal)
        to_visit_price.append(price)
    for i in range(len(to_visit_link)):
        scrape_individual(to_visit_link[i], to_visit_street[i], to_visit_city[i], to_visit_region[i], to_visit_postal[i], to_visit_price[i])
        
def scrape_individual(each_link, street, city, region, postal, price):
    browser.get(each_link)
    time.sleep(10)

    try:
        property_internals = browser.find_element_by_id("ldp-property-meta")
    except:
        property_internals = ""

    if property_internals != "":
        print "inside property internals"
        required_content = property_internals.text
        required_content.replace('\n', '')

        try:
            beds, required_content = required_content.split('beds')
            
        except:
            beds = ""

        try:
            baths, required_content = required_content.split('baths')
        except:
            baths = ""

        try:
            sqft, required_content = required_content.split('sq ft')
        except:
            sqft = ""

        try:
            lotsize, required_content = required_content.split('acres')
        except:
            lotsize = ""
        '''
        try:
            beds_li = property_internals.find_element_by_xpath("//li[@data-label='property-meta-beds']")
            beds = beds_li.find_element_by_class_name("data-value").text
        except:
            beds = ""
        try:
            baths_li = property_internals.find_element_by_xpath("//li[@data-label='property-meta-baths']")
            baths = baths_li.find_element_by_class_name("data-value").text
        except:
            baths = ""
        try:
            sqft_li = property_internals.find_element_by_xpath("//li[@data-label='property-meta-sqft']")
            sqft = sqft_li.find_element_by_class_name("data-value").text
        except:
            sqft = ""
        try:
            lotsize_li = property_internals.find_element_by_xpath("//li[@data-label='property-meta-lotsize']")
            lotsize = lotsize_li.find_element_by_class_name("data-value").text
        except:
            lotsize = ""
        '''
    else:
        beds = ""
        baths = ""
        sqft = ""
        lotsize = ""
    
    try:
        desc = browser.find_element_by_id("ldp-detail-romance").text
    except:
        desc = ""
#    csvwriter.writerow([street, city, region, postal, street+city+region, price, beds, baths, sqft, lotsize, property_type, broker])

    try:
        broker_agent_div = browser.find_element_by_id("ldp-agentbroker-attribution")
    except:
        broker_agent_div = ""
    if broker_agent_div != "":
        try:
            broker_agent = broker_agent_div.find_elements_by_class_name("font-bold")
            agent_name = (broker_agent[0]).text
            broker_name = (broker_agent[1]).text
        except:
            agent_name = ""
            broker_name = ""  
    else:
        agent_name = ""
        broker_name = ""

    
    try:
        year_built_div = browser.find_element_by_id("ldp-detail-overview")
        year_built_ul = year_built_div.find_element_by_tag_name("ul")
        year_built = year_built_ul.find_element_by_xpath("//li[@data-label='property-year']")
        year_built = year_built.text
    except:
        year_built = ""
    try:
        property_type_info = year_built_div.find_element_by_tag_name("ul") 
        property_type_info = property_type_info.find_element_by_xpath("//li[@data-label='property-type']")
        property_type_info = property_type_info.text
    except:
        property_type_info = ""


    try:
        business_card_content = browser.find_element_by_class_name("business-card-content") 
        agent_website = business_card_content.find_element_by_partial_link_text('View Agent')
        agent_website = agent_website.get_attribute("href")
    except:
        agent_website = "" 

    try:
        property_history = browser.find_element_by_id("ldp-history-price")
        sdate = property_history.find_element_by_tag_name("td").text
    except:
        sdate = ""

    try:
        listing_provider = browser.find_element_by_id("ldp-listing-provider")
        msid = listing_provider.find_element_by_xpath("//td[@itemprop='productID']")
        msid = msid.text
    except:
        msid = ""

    try:
        images_div = browser.find_element_by_id("ldpPhotos")
        images = images_div.find_elements_by_tag_name('img')
        final_image = ""
        images = [each_image.get_attribute("src") for each_image in images]
        print images
        img_count = 0
        for each_image in images:
            if each_image != "":
                final_image = final_image + each_image + "^"
                img_count += 1
            if img_count == 5:
                break
    except:
        images = ""
        final_image = ""

    list_id = ""
    title = ""


    #make a list of property details depicting table fields and send the value as param to insert_property. We are done then. 
    property_details_list = [list_id, msid, title, price, desc, street, city, region, postal, "New", beds, baths, year_built, lotsize, sqft, agent_name, broker_name, agent_website, sdate, final_image]
    insert_property(property_details_list)
    print property_details_list

def main(url, first_run=True):
    global browser
    browser.get(url)
    time.sleep(10)
    results_per_page = browser.find_element_by_id("srp-select-count")
    for option in results_per_page.find_elements_by_tag_name('option'):
        if option.text == "50":
            option.click()

    time.sleep(7)
    if first_run:
        pagination_div = browser.find_element_by_class_name("pagination")
        span_tags = pagination_div.find_elements_by_tag_name("span")
        req_span = span_tags[-2]
        total_pagination = req_span.find_element_by_tag_name('a').text
    
        total_pagination = int(total_pagination)
    
    content_div = browser.find_element_by_class_name("srp-list-marginless")

    all_individual_contents = content_div.find_elements_by_class_name("js-record-user-activity")
    print len(all_individual_contents)
    get_essential_info(all_individual_contents)
    
    if first_run:
        for i in range(1, total_pagination + 1):
            new_url = url.replace("pg-" + str(i), "pg-" + str(i+1))
            browser.quit()
            chrome_options = webdriver.ChromeOptions()
            select_proxy_index = i % len(proxies_list)
            select_proxy = proxies_list[select_proxy_index]
            chrome_options.add_argument('--proxy-server=%s' % select_proxy)
            browser = webdriver.Chrome(executable_path='C:\Users\Administrator\Downloads\chromedriver_win32\chromedriver.exe', chrome_options=chrome_options)
            main(new_url, False)

if __name__ == '__main__':
    urls = ["http://www.realtor.com/realestateandhomes-search/33957/shw-nl/pg-1?nzp=33956,33914,33931,33908,33904,33919,33990,33907,33912,33901,34134,33967,33966,34110,34108,34135,34109,34103,34105"]
    for each_url in urls:
        main(each_url)
