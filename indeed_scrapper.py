from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

class Job:
	def __init__(self, title, link, company_name, location, salary, short_description):
		self.title = title
		self.link = link
		self.company_name = company_name
		self.location = location
		self.salary = salary
		self.short_description = short_description
		self.long_description = None

def get_long_description(browser, url):
	print("Get long...")
	browser.get(url)
	long_description_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "jobDescriptionText")))
	long_description = long_description_element.text
	return long_description

def get_data(browser, url):
	browser.get(url)
	print("waiting...")
	jobs = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jobCard_mainContent")))
	job_instances = []

	for job in jobs:
		try:
			job_title_element = job.find_element(By.CLASS_NAME, "jobTitle")
			job_title = job_title_element.find_element(By.TAG_NAME, "a").get_attribute("title")
			job_link = job_title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
			company_name = job.find_element(By.CLASS_NAME, "companyName").text
			location = job.find_element(By.CLASS_NAME, "companyLocation").text
			salary_elements = job.find_elements(By.CSS_SELECTOR, ".metadata .attribute_snippet")
			salary = salary_elements[0].text if salary_elements else "Not provided"
			short_description_elements = job.find_elements(By.CSS_SELECTOR, ".job-snippet ul li")
			short_description = " ".join([desc_elem.text for desc_elem in short_description_elements]) if short_description_elements else "Not provided"
			
			job_instance = Job(job_title, job_link, company_name, location, salary, short_description)
			print(f"Company Name:{company_name}\nTitle:{job_title}\n\n")
			job_instances.append(job_instance)
		except Exception as e:
			print(f"An error occurred: {e}")

	return job_instances

# driver nodes/main function
if __name__ == "__main__":
	options = Options()
	options.binary_location = '/opt/firefox/firefox'
	browser = webdriver.Firefox(options=options)
	
	job = "Software Engineer"
	Location = "Remote"
	url = "https://www.indeed.com/jobs?q=" + job + "&l=" + Location

	# Call get_data function and store the results
	job_instances = get_data(browser, url)

	# Traverse the job instances and get the long description
	for job_instance in job_instances:
		job_instance.long_description = get_long_description(browser, job_instance.link)
		print(f"Job Title: {job_instance.title}")
		print(f"Short Description: {job_instance.short_description}")
		print(f"Long Description: {job_instance.long_description}\n")
		
	browser.quit()
