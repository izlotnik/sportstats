import csv
from selenium import webdriver
import time


PATH_TO_CHROME_DRIVER = 'chromedriver.exe'
if __name__ == "__main__":
    start_url = "https://www.sportstats.ca/display-results.xhtml?raceid=44616"
    sleep_time_sec = 1

    with open('demo_detail.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';', quoting=csv.QUOTE_ALL)

        # Add header
        header = ["COMP.", "VIEW", "RANK", "BIB", "NAME", "CITY", "CATEGORY", "CAT. PLACE", "OFFICIAL TIME",
                  "SPLIT NAME", "SPLIT DISTANCE", "SPLIT TIME", "PACE", "DISTANCE", "RACE TIME", "OVERALL", "GENDER",
                  "CATEGORY", "TIME OF DAY"]
        csv_writer.writerow(header)

        # Define Chrome web driver
        driver = webdriver.Chrome(PATH_TO_CHROME_DRIVER)

        try:
            driver.get(start_url)
            table_tr = driver.find_elements_by_xpath("//table[@class='results overview-result']/tbody/tr[@role='row']")

            # Iterate through each row of the main table
            count = 0
            for tr in table_tr:
                lst = []

                # Parse the main table rows
                table_td = tr.find_elements_by_tag_name("td")
                for td in table_td:
                    lst.append(td.text)

                # Click on the second element in the table ("VIEW") to expand the table and wait for 5 sec
                table_td[1].find_element_by_tag_name("div").click()
                time.sleep(sleep_time_sec)

                # Parse the expanded table rows
                for demo_tr in driver.find_elements_by_xpath(
                        "//tr[@class='ui-expanded-row-content ui-widget-content view-details']/td/div/div/table/tbody/tr"):
                    for demo_td in demo_tr.find_elements_by_tag_name("td"):
                        lst.append(demo_td.text)
                csv_writer.writerow(lst)

                # Click again on the view to fold it
                table_td[1].find_element_by_tag_name("div").click()
                time.sleep(sleep_time_sec)

                # Print the result
                count += 1
                print(count, lst)

        except Exception as e:
            print(e)
        finally:
            driver.quit()
