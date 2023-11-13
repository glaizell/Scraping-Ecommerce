from selenium import webdriver
from fake_useragent import UserAgent
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

ua = UserAgent(os='linux', browsers=['edge', 'chrome'], min_percentage=1.3)
random_user_agent = ua.random

# Keep the browser open after the program finishes
options = Options()
options.add_experimental_option("detach", True)
options.add_argument(f"user-agent={random_user_agent}")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()

scraped_data = []


def scrape_page_content(items):
    for item in items:
        name = item.find_element(By.CSS_SELECTOR, ".gl-product-card__details-main span.gl-product-card__name").text

        # Use a try-except block to handle the absence of the price element
        try:
            price = item.find_element(By.CSS_SELECTOR, '.gl-price-item.gl-price-item--small.gl-product-card__price')
            price_text = price.text
        except NoSuchElementException:
            price_text = "Price not available"

        img_element = item.find_element(By.CSS_SELECTOR, 'div.Image img')
        image_url = img_element.get_attribute('src')

        if name and image_url:
            print("Image URL:", image_url)
            print(name)
            print(price_text)
            print("==============================================\n")

            # Append data to the list for pandas
            data = {
                "Image_URL": image_url,
                "Name": name,
                "Price": price_text,
            }
            scraped_data.append(data)
        else:
            print("Not available")


# Iterate over both pages
for page_number in range(1, 3):  # Adjust the range based on the number of pages you want to scrape
    url = f"https://www.adidas.co.id/pria/sepatu/sepak-bola.html?page={page_number}"
    driver.get(url)

    # Wait for the element to be present before trying to interact with it
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "ProductListPage"))
        WebDriverWait(driver, 10).until(element_present)

    except TimeoutError as e:
        print(f"Time out waiting : {e}")

    wait = WebDriverWait(driver, 10)

    container_div = driver.find_elements(By.CLASS_NAME, value="ProductCard")
    scrape_page_content(container_div)



# Create a DataFrame from the list of dictionaries
df = pd.DataFrame(scraped_data, columns=["Image_URL", "Price", "Name"], index=range(1, len(scraped_data) + 1))

# Print the DataFrame
print(df)

print("Before saving CSV")
# Save the DataFrame to a CSV file
df.to_csv("scraped_data.csv", index_label="No")
print("After saving CSV")
driver.quit()
