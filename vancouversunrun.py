import csv
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# import time


PATH_TO_CHROME_DRIVER = 'chromedriver.exe'

if __name__ == "__main__":
    # Set the URL to start
    start_url = "https://www.sportstats.ca/display-results.xhtml?raceid=44616"

    # Set maximum sleeping time
    sleep_time_sec = 3

    # Define main xpath queries
    main_table_xpath = "//table[@class='results overview-result']"
    expanded_table_xpath = "//tr[@class='ui-expanded-row-content ui-widget-content view-details']"
    athlete_table_xpath = "//div[@id='athlete-popup']"

    with open('results.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_ALL)

        # Define Chrome web driver
        browser = webdriver.Chrome(PATH_TO_CHROME_DRIVER)
        browser.maximize_window()
        # browser.implicitly_wait(sleep_time_sec)
        try:
            browser.get(start_url)
            main_table = browser.find_element_by_xpath(main_table_xpath)

            # Get the header of the main table
            main_header = []
            for th in main_table.find_elements_by_xpath("//thead/tr/th/span/span"):
                main_header.append(th.text)

            # Iterate through each row of the main table
            for row_id, row in enumerate(main_table.find_elements_by_xpath("//tbody/tr")):
                # Parse the main table rows
                try:
                    table_td = row.find_elements_by_tag_name("td")
                    total_info = []
                    for jdx, td in enumerate(table_td):
                        total_info.append((main_header[jdx], td.text))
                except StaleElementReferenceException as e:
                    break

                # Click on the second element in the table ("VIEW") to expand the table and wait for 5 sec
                table_td[1].find_element_by_tag_name("div").click()
                # time.sleep(sleep_time_sec)

                # Locate the expanded table
                # expanded_table = browser.find_element_by_xpath(expanded_table_xpath)
                expanded_table = WebDriverWait(browser, sleep_time_sec).until(
                    EC.presence_of_element_located((By.XPATH, expanded_table_xpath)))

                # Get the header of the expanded table
                expanded_header = []
                for th in expanded_table.find_elements_by_xpath("//td/div/div/table/thead/tr/th/span"):
                    expanded_header.append(th.text)

                # Parse the expanded table rows
                expanded_info = []
                for expanded_tr in expanded_table.find_elements_by_xpath("//td/div/div/table/tbody/tr"):
                    split_info = []
                    for jdx, expanded_td in enumerate(expanded_tr.find_elements_by_tag_name("td")):
                        split_info.append((expanded_header[jdx], expanded_td.text))
                    expanded_info.append(split_info)

                # Parse athlete popup table summary
                # athlete_table = browser.find_element_by_xpath(athlete_table_xpath)
                athlete_table = WebDriverWait(browser, sleep_time_sec).until(
                    EC.visibility_of_element_located((By.XPATH, athlete_table_xpath)))
                athlete_info = [("FULL NAME", athlete_table.find_element_by_xpath("//div/div/h3").text)]
                for athlete_tr in athlete_table.find_elements_by_xpath("//div/div[@id='athlete-content']/table/tbody/tr"):
                    athlete_td = athlete_tr.find_elements_by_tag_name("td")
                    if len(athlete_td) == 2:
                        athlete_info.append((athlete_td[0].text, athlete_td[1].text))

                # Click again on the view to fold it and wait until closed
                table_td[1].find_element_by_tag_name("div").click()
                # time.sleep(sleep_time_sec)
                _ = WebDriverWait(browser, sleep_time_sec).until_not(
                    EC.visibility_of_element_located((By.XPATH, athlete_table_xpath)))

                # Print the result
                print(row_id+1, total_info, expanded_info, athlete_info, sep='\n')

                # TODO: Save output lists total_info, expanded_info, athlete_info to the file
                # csv_writer.writerow(lst)

        except Exception as e:
            print(e)
        finally:
            browser.quit()
