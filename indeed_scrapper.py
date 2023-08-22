from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

def get_data(url):
    options = Options()
    options.binary_location = '/opt/firefox/firefox'
    browser = webdriver.Firefox(options=options)
    browser.get(url)
    print("waiting...")
    jobs = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jobCard_mainContent")))

    for job in jobs:
        try:
            job_title_element = job.find_element(By.CLASS_NAME, "jobTitle")
            job_title = job_title_element.find_element(By.TAG_NAME, "a").get_attribute("title")
            job_link = job_title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            company_name = job.find_element(By.CLASS_NAME, "companyName").text
            location = job.find_element(By.CLASS_NAME, "companyLocation").text
            
            # Check if salary is present
            salary_elements = job.find_elements(By.CSS_SELECTOR, ".metadata .attribute_snippet")
            salary = salary_elements[0].text if salary_elements else "Not provided"
            
            # Check if job description is present
            job_description_elements = job.find_elements(By.CSS_SELECTOR, ".job-snippet ul li")
            job_description = " ".join([desc_elem.text for desc_elem in job_description_elements]) if job_description_elements else "Not provided"

            print(f"Job Title: {job_title}")
            print(f"Job Link: {job_link}")
            print(f"Company Name: {company_name}")
            print(f"Location: {location}")
            print(f"Salary: {salary}")
            print(f"Job Description: {job_description}\n")
        except Exception as e:
            print(f"An error occurred: {e}")

    browser.quit()

# driver nodes/main function
if __name__ == "__main__":
    job = "Software Engineer"
    Location = "Remote"
    url = "https://www.indeed.com/jobs?q=" + job + "&l=" + Location

    # Call get_data function
    get_data(url)
