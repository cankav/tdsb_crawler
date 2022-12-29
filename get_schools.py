from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
import time
import pandas as pd
import sys
from selenium.common.exceptions import NoSuchElementException

df = pd.DataFrame(columns=['url', 'code', 'name', 'total_language_data_available', 'total_students', 'JK_GR3', 'GR4_GR6', 'GR7_GR8', 'female', 'male', 'primary_not_english', 'living_in_canada_less_than_2_years', 'living_in_canada_for_3_5_years'])

driver = Chrome('./chromedriver')
driver.get('https://www.tdsb.on.ca/Find-your/School/By-School-Name/Elementary')

def scroll_to_bottom():
    SCROLL_PAUSE_TIME = 5
    # from https://stackoverflow.com/a/27760083/1056345
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


all_schools = driver.find_elements(By.CSS_SELECTOR, '[class="schoolList"]')
for school_index, school in enumerate(all_schools):
    print('\n\nschool_index', school_index, school.text)
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

print(df)
print(df.shape)

def get_element_by_id(driver, element_text):

    # 1) find line number of given text
    # 2) look up value by id using dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_+line_number
    try:
        xpath_str = f"//strong[contains(text(),'{element_text}')]//parent::span"
        print('\n\nxpath_str', xpath_str)
        row_title_id = driver.find_element(By.XPATH, xpath_str).get_attribute('id')

    except NoSuchElementException:
        try:
            print(element_text, 'not found, trying without strong')
            xpath_str = f"//span[contains(text(),'{element_text}')]"
            print('xpath_str', xpath_str)
            row_title_id = driver.find_element(By.XPATH, xpath_str).get_attribute('id')

        except NoSuchElementException:
            print(element_text, 'not found, giving up')
            return None


    row_title_numeric_id = int(row_title_id.split('_')[-1])
    val = driver.find_element(By.ID, f"dnn_ctr2930_ViewSPC_ctl00_rptFacts_lblFactsRight_{str(row_title_numeric_id)}").text
    print('found', element_text, val)
    return val

        
    
for index, row in df.iterrows():
    print('index', index, 'out of', df.shape[0])
    driver.get(f"https://www.tdsb.on.ca/Find-your/Schools/Facts-and-Figures/schno/{row.code}")
    df.loc[index, 'total_students'] = get_element_by_id( driver,  'Total number of students')
    df.loc[index, 'total_language_data_available'] = get_element_by_id( driver,  'Total language data available')
    df.loc[index, 'JK_GR3'] = get_element_by_id( driver,  'Junior Kindergarten - Grade 3')
    df.loc[index, 'GR4_GR6'] = get_element_by_id( driver,  'Grade 4 - Grade 6')
    df.loc[index, 'GR7_GR8'] = get_element_by_id( driver,  'Grade 7 - Grade 8')
    df.loc[index, 'female'] = get_element_by_id( driver,  'Female')
    df.loc[index, 'male'] = get_element_by_id( driver,  'Male')
    df.loc[index, 'primary_not_english'] = get_element_by_id( driver,  'Primary language other than English')
    df.loc[index, 'living_in_canada_less_than_2_years'] = get_element_by_id( driver,  'Students living in Canada for 2 years or less')
    df.loc[index, 'living_in_canada_for_3_5_years'] = get_element_by_id( driver,  'Students living in Canada for 3 - 5 years')
    time.sleep(1)

print('final df')    
print(df.T.to_string())

df.to_csv(f"school_data0.csv", index=False)

driver.close()
