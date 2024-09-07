from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
from selenium.common.exceptions import NoSuchElementException

# Set the path to your ChromeDriver (replace with your actual path)
driver_path = "/Users/ajay_manhota/Documents/chromedriver-mac-x64/chromedriver"

# Initialize the WebDriver using the Service object
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Function to accept cookie consent banner
def accept_cookies():
    try:
        # Wait for and click the "Accept Cookies" button if it exists
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_button.click()
        print("Accepted cookies.")
    except NoSuchElementException:
        print("No cookie banner found.")
    except Exception as e:
        print(f"Error accepting cookies: {e}")

# Function to search Rotten Tomatoes using the movie title and click on the first search result
def search_and_click_rotten_tomatoes(movie_title):
    search_url = f"https://www.rottentomatoes.com/search?search={movie_title.replace(' ', '%20')}"
    driver.get(search_url)

    time.sleep(2)  # Allow the page to load
    
    # Accept the cookie consent banner if present
    accept_cookies()

    # Wait for the search results to appear and find the first result
    try:
        first_result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "search-page-media-row a"))
        )
        first_result.click()  # Click on the first search result

        # Wait for the URL to change, confirming a successful navigation
        WebDriverWait(driver, 10).until(
            EC.url_changes(search_url)
        )
        
    except Exception as e:
        print(f"Error clicking on the first search result: {e}")
        return None
    
    # Allow the page to load after clicking
    time.sleep(2)

    # Return the current URL after clicking into the movie's page
    return driver.current_url

# Function to scrape Popcorn Meter (Audience) score from the movie page
def get_popcorn_meter_score(movie_title):
    movie_url = search_and_click_rotten_tomatoes(movie_title)
    
    if not movie_url:
        print(f"Movie not found on Rotten Tomatoes: {movie_title}")
        return "N/A"

    # Wait for the movie page to load
    try:
        # Wait specifically for the rt-text element (or similar) to appear before scraping
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'rt-text'))
        )
    except Exception as e:
        print(f"Error waiting for score element to load: {e}")
        return "N/A"
    
    # Parse the movie page with BeautifulSoup after clicking into the page
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Print the page URL and part of the page source for debugging
    print(f"Currently on URL: {movie_url}")
    print("Page Source Sample (first 500 characters):")
    print(soup.prettify()[:500])  # Print the first 500 characters of the page source

    # Find the 'rt-text' tag that contains the Audience Score on the movie's page
    audience_score_element = soup.find('rt-text', context='label')  # Adjust this based on the actual tag and attributes
    
    if audience_score_element:
        audience_score = audience_score_element.text.strip()  # Extract the text (e.g., '62%')
        print(f"Popcorn Meter (Audience Score) for {movie_title}: {audience_score}")
        return audience_score
    
    return "N/A"

# Full path to your CSV file
input_csv = "/Users/ajay_manhota/Documents/Python/movies.csv"
output_csv = "/Users/ajay_manhota/Documents/Python/popcorn_scores.csv"

# Function to read movie titles from CSV and scrape Popcorn Meter scores
def scrape_movies(input_csv, output_csv):
    try:
        with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            writer.writerow(['Movie Title', 'Popcorn Meter (Audience Score)'])  # Write the header

            for row in reader:
                movie_title = row[0]
                print(f"Fetching score for: {movie_title}")
                popcorn_score = get_popcorn_meter_score(movie_title)
                writer.writerow([movie_title, popcorn_score])
                
                # Clear cookies and cache between each movie to avoid interference
                driver.delete_all_cookies()
                
    except FileNotFoundError as e:
        print(f"Error: {e}")

# Main script execution
if __name__ == "__main__":
    scrape_movies(input_csv, output_csv)

# Close the WebDriver after scraping is complete
driver.quit()
