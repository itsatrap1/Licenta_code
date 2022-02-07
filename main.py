from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

url = r'https://www.skiresort.info/ski-resorts/'

browser = webdriver.Chrome(ChromeDriverManager().install())
browser_ski_lifts = webdriver.Chrome(ChromeDriverManager().install())

all_l = []
resort_links = []

for i in range(1, 2):
    p_url = url + 'page' + '/' + str(i) + '/'
    browser.get(p_url)

    all_resort_per_page = browser.find_element(By.ID, 'resortList')

    links = all_resort_per_page.find_elements(By.CSS_SELECTOR, 'div.h3 > a')
    for el in links:
        resort_links.append(el.get_attribute('href'))

lift_names_and_numbers = [[] for el in resort_links]
full_lift_names = []

slope_difficulty_web_elements = []
slope_length_web_elements = []
slope_difficulty = []
slope_length = [[] for el in resort_links]
altitude = []


price_adults = []
price_youth = []
price_children = []
resort_names = []
first_lift_table = []

for i in range(len(resort_links)):    # SKI-LIFT DETAILS

    browser_ski_lifts.get(resort_links[i] + 'ski-lifts')
    browser.get(resort_links[i])

    index = resort_links[i].find('t/')
    name = resort_links[i][index + 2:len(resort_links[i]) - 1]
    resort_names.append(name)
    try:
        first_lift_table = browser_ski_lifts.find_element(By.ID, 'expandable-box-resort')
        lift_number_web_elements = first_lift_table.find_elements(By.CLASS_NAME, 'lift-number')
        lift_name_web_elements = first_lift_table.find_elements(By.CLASS_NAME, 'lift-name')
        for k in range(len(lift_number_web_elements)):

            if lift_name_web_elements[k].text not in full_lift_names:
                full_lift_names.append(lift_name_web_elements[k].text)

            if lift_number_web_elements[k].text != '' and lift_name_web_elements[k].text != ' ':
                lift_names_and_numbers[i].append([lift_number_web_elements[k].text, lift_name_web_elements[k].text])

    except NoSuchElementException:
        print('None')

    slope_altitude_web_elements = browser.find_elements(By.ID, 'selAlti')

    if len(slope_altitude_web_elements) == 0:
        x = '0 m - 0 m (Difference 0 m)'
        altitude.append(x)
    else:
        altitude.append(slope_altitude_web_elements[0].text)

    slope_difficulty_web_elements = browser.find_elements(By.CLASS_NAME, 'desc')
    slope_difficulty = [el.text for el in slope_difficulty_web_elements for i in range(1)]

    slope_length_web_elements = browser.find_elements(By.CLASS_NAME, 'distance')
    for k in range(len(slope_length_web_elements)):
        if k != 3:
            slope_length[i].append(slope_length_web_elements[k].text)

    try:
        adults = browser.find_element(By.ID, 'selTicketA')
        i = adults.text.find(',')
        a = adults.text[:i]
        price_adults.append(a)
    except NoSuchElementException:
        adults = '0'
        price_adults.append(adults)
    try:
        youth = browser.find_element(By.ID, 'selTicketY')
        i = youth.text.find(',')
        y = youth.text[:i]
        price_youth.append(y)
    except NoSuchElementException:
        youth = '0'
        price_youth.append(youth)
    try:
        child = browser.find_element(By.ID, 'selTicketC')
        i = child.text.find(',')
        c = child.text[:i]
        price_children.append(c)
    except NoSuchElementException:
        child = '0'
        price_children.append(child)


non_existing_lifts_list = [[] for el in lift_names_and_numbers]


for k in range(len(lift_names_and_numbers)):
    names = [elements[1] for elements in lift_names_and_numbers[k]]
    for name in full_lift_names:
        if name not in names and name != '':
            non_existing_lifts_list[k].append(['0', name])


for i in range(len(non_existing_lifts_list)):
    for j in range(len(non_existing_lifts_list[i])):
        lift_names_and_numbers[i].append(non_existing_lifts_list[i][j])


lift_names_and_numbers_dictionary = {}

for el in full_lift_names:
    lift_names_and_numbers_dictionary[el] = []

for el in lift_names_and_numbers:
    for i in range(len(el)):
        lift_names_and_numbers_dictionary[el[i][1]].append(el[i][0])

lift_names_and_numbers_dictionary.pop('')

for el in slope_length:
    if len(el) < 3:
        for i in range(3-len(el)):
            el.append('0')


if len(slope_difficulty) == 4:
    slope_difficulty = slope_difficulty[:3]

slope_altitude_list = [[number for number in el.split() if number.isdigit()] for el in altitude]


full_dictionary = {'Name': [el for el in resort_names],
                   'Lowest point': [el[0] for el in slope_altitude_list],
                   'Highest point': [el[1] for el in slope_altitude_list],
                   'Difference': [el[2] for el in slope_altitude_list]}


slope_difficulty_dictionary = {}
ski_pass_prices_dictionary = {}

for el in slope_difficulty:
    slope_difficulty_dictionary[el] = []

for i in range(len(slope_difficulty)):
    for j in range(len(slope_length)):
        slope_difficulty_dictionary[slope_difficulty[i]].append(slope_length[j][i])


prices = [[price_adults[i], price_youth[i], price_children[i]] for i in range(len(price_adults))]


ski_pass_prices_dictionary = {'Adult ticket price': [el[0] for el in prices],
                              'Youth ticket price': [el[1] for el in prices],
                              'Children ticket price': [el[2] for el in prices]}

full_dictionary.update(slope_difficulty_dictionary)
full_dictionary.update(ski_pass_prices_dictionary)
full_dictionary.update(lift_names_and_numbers_dictionary)

data_frame = pd.DataFrame(full_dictionary)

data_frame.to_csv('date3.xls', mode = 'a', encoding = 'utf-16')








