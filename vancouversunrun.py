import csv
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import uuid


def get_next_page(driver, next_page_num, freezing_time):
    # nav_pages = driver.find_elements_by_xpath("//div[@id='mainForm:pageNav']/div/ul/li")
    nav_pages = WebDriverWait(driver, freezing_time).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@id='mainForm:pageNav']/div/ul/li")))

    # Get first, active and last page numbers
    first_page_num = int(nav_pages[2].find_element_by_tag_name("a").text)
    active_page_num = int(driver.find_element_by_xpath(
        "//div[@id='mainForm:pageNav']/div/ul/li[@class='active']/a").text)
    last_page_num = int(nav_pages[-3].find_element_by_tag_name("a").text)

    if next_page_num <= active_page_num:
        return

    if next_page_num <= last_page_num:
        nav_pages[next_page_num - first_page_num + 2].find_element_by_tag_name("a").click()
        time.sleep(freezing_time)

        return
    else:
        nav_pages[-3].find_element_by_tag_name("a").click()
        time.sleep(freezing_time)

        get_next_page(driver, next_page_num, freezing_time)


PATH_TO_CHROME_DRIVER = 'chromedriver.exe'

if __name__ == "__main__":
    # Set the URL to start
    start_url = "https://www.sportstats.ca/display-results.xhtml?raceid=44616"
    first_page = 50
    restart_page = 5

    # Set maximum sleeping time
    sleep_time_sec = 5

    # Define main table xpath queries
    main_table_xpath = "//table[@class='results overview-result']"
    expanded_table_xpath = "//tr[@class='ui-expanded-row-content ui-widget-content view-details']"
    athlete_table_xpath = "//div[@id='athlete-popup']"

    # with open('results.csv', 'w', newline='') as csv_file:
    with open('results_main.csv', 'w', newline='', encoding="utf-8") as main_file, \
            open('results_expanded.csv', 'w', newline='', encoding="utf-8") as expanded_file, \
            open('results_athlete.csv', 'w', newline='', encoding="utf-8") as athlete_file:
        # Set writers
        wr_main = csv.writer(main_file, delimiter=';', quoting=csv.QUOTE_ALL)
        wr_expanded = csv.writer(expanded_file, delimiter=';', quoting=csv.QUOTE_ALL)
        wr_athlete = csv.writer(athlete_file, delimiter=';', quoting=csv.QUOTE_ALL)

        try:
            row_id, count = 1, 0
            while True:
                if count == 0 or count % ((row_id-1) * restart_page) == 0:
                    if count > 0:
                        print("Close the browser")
                        browser.quit()

                    # Define Chrome web driver
                    browser = webdriver.Chrome(PATH_TO_CHROME_DRIVER)
                    browser.maximize_window()
                    # browser.implicitly_wait(sleep_time_sec)
                    browser.get(start_url)
                    get_next_page(browser, first_page, sleep_time_sec)

                #
                main_table = browser.find_element_by_xpath(main_table_xpath)

                # Get the header of the main table and save it
                if count == 0:
                    main_header = ["UID"]
                    for th in main_table.find_elements_by_xpath("//thead/tr/th/span/span"):
                        main_header.append(th.text)
                    wr_main.writerow(main_header)

                # Iterate through each row of the main table
                for row_id, row in enumerate(main_table.find_elements_by_xpath("//tbody/tr"), 1):
                    # Get unique id for each row of the table
                    uid = uuid.uuid4().hex

                    # Parse the main table rows and save them
                    try:
                        table_td = row.find_elements_by_tag_name("td")
                        main_info = [uid]
                        for td in table_td:  # for jdx, td in enumerate(table_td):
                            main_info.append(td.text)  # main_info.append((main_header[jdx], td.text))
                        wr_main.writerow(main_info)
                    except StaleElementReferenceException as e:
                        break

                    # Click on the second element in the table ("VIEW") to expand the table and wait for 5 sec
                    table_td[1].find_element_by_tag_name("div").click()

                    # Locate the expanded table
                    # expanded_table = browser.find_element_by_xpath(expanded_table_xpath)
                    expanded_table = WebDriverWait(browser, sleep_time_sec).until(
                        EC.presence_of_element_located((By.XPATH, expanded_table_xpath)))

                    # Get the header of the expanded table and save it
                    if count == 0:
                        expanded_header = ["UID", "SPLIT ID"]
                        for th in expanded_table.find_elements_by_xpath("//td/div/div/table/thead/tr/th/span"):
                            expanded_header.append(th.text)
                        wr_expanded.writerow(expanded_header)

                    # Parse the expanded table rows
                    for split_id, expanded_tr in enumerate(
                            expanded_table.find_elements_by_xpath("//td/div/div/table/tbody/tr")):
                        split_info = [uid, split_id]
                        for expanded_td in expanded_tr.find_elements_by_tag_name("td"):
                            split_info.append(expanded_td.text)
                        wr_expanded.writerow(split_info)

                    # Parse athlete popup table summary
                    # athlete_table = browser.find_element_by_xpath(athlete_table_xpath)
                    athlete_table = WebDriverWait(browser, sleep_time_sec).until(
                        EC.visibility_of_element_located((By.XPATH, athlete_table_xpath)))
                    athlete_header = ["UID", "NAME"]
                    athlete_info = [uid, athlete_table.find_element_by_xpath("//div/div/h3").text]
                    for athlete_tr in athlete_table.find_elements_by_xpath(
                            "//div/div[@id='athlete-content']/table/tbody/tr"):
                        athlete_td = athlete_tr.find_elements_by_tag_name("td")
                        if len(athlete_td) == 2:
                            athlete_header.append(athlete_td[0].text)
                            athlete_info.append(athlete_td[1].text)
                    # Save the table
                    if count == 0:
                        wr_athlete.writerow(athlete_header)
                    wr_athlete.writerow(athlete_info)

                    # Click again on the view to fold it and wait until closed
                    table_td[1].find_element_by_tag_name("div").click()
                    _ = WebDriverWait(browser, sleep_time_sec).until_not(
                        EC.visibility_of_element_located((By.XPATH, athlete_table_xpath)))

                    # Next iteration
                    count += 1

                    # Print the result
                    print(row_id, count, sep='\n')  # , main_info, athlete_info

                # Load next page
                first_page += 1
                get_next_page(browser, first_page, sleep_time_sec)

        except Exception as e:
            print(e)
        finally:
            browser.quit()
