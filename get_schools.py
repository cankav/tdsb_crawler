from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import time
import pandas as pd
import sys
from selenium.common.exceptions import NoSuchElementException

df = pd.DataFrame(columns=['url', 'code', 'name', 'total_students', 'JK_GR3', 'GR4_GR6', 'GR7_GR8', 'female', 'male', 'primary_not_english', 'living_in_canada_less_than_2_years', 'living_in_canada_for_3_5_years'])

driver = Chrome('./chromedriver')
driver.get('https://www.tdsb.on.ca/Find-your/School/By-School-Name/Elementary')

letter = driver.find_element(By.ID, 'dnn_ctr1678_SchoolSearch_rptLetterNav_lnkLetter_1')
letter.click()

all_schools = driver.find_elements(By.CSS_SELECTOR, '[class="schoolList"]')
for school in all_schools:
    link = school.find_element(By.TAG_NAME, 'a')
    url = link.get_attribute('href')
    name = link.text
    code = url.split('=')[1]
    row = {
        'url': url,
        'code': code,
        'name': name
    }

    df = pd.concat(
        [
            df,
            pd.DataFrame.from_dict(row, orient='index').T
        ],
        ignore_index=True)
    break

def get_element_by_id(driver, element_id):

    # 1) find line number of given text
    # 2) look up value by id using dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_+line_number
    try:
        val = driver.find_element(By.ID, element_id).text
        print(element_id, val)
        return val
    except NoSuchElementException:
        print(element_id, 'not found')
        return None
    
for index, row in df.iterrows():
    print('here',row)
    driver.get(f"https://www.tdsb.on.ca/Find-your/Schools/Facts-and-Figures/schno/{row.code}")
    df.loc[index, 'total_students'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_2')
    df.loc[index, 'JK_GR3'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsLeft_3')
    df.loc[index, 'GR4_GR6'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_4')
    df.loc[index, 'GR7_GR8'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_5')
    df.loc[index, 'female'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_7')
    df.loc[index, 'male'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_8')
    df.loc[index, 'primary_not_english'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_11')
    df.loc[index, 'living_in_canada_less_than_2_years'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_14')
    df.loc[index, 'living_in_canada_for_3_5_years'] = get_element_by_id( driver,  'dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_15')

print('final df')    
print(df.T.to_string())

time.sleep(10)
driver.close()
