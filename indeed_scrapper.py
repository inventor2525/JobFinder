import os
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

class Job:
	def __init__(self, title, link, company_name, location, salary, short_description, date_posted):
		self.title = title
		self.link = link
		self.company_name = company_name
		self.location = location
		self.salary = salary
		self.short_description = short_description
		self.date_posted = date_posted
		self.long_description = None
		
def sanitize_filename(filename):
	return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

class IndeedScraper:
	def __init__(self, job, location):
		self.job = job
		self.location = location
		self.base_url = f"https://www.indeed.com/jobs?q={job}&l={location}&sort=date"
		self.start_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")
		self.page_num = 1
		
		options = Options()
		options.binary_location = '/opt/firefox/firefox'
		self.browser = webdriver.Firefox(options=options)
		self.next_page_available = False

		# Directory structure
		self.base_dir = f"Job_Data/{sanitize_filename(job)}/{sanitize_filename(location)}/{self.start_time}/"
		os.makedirs(self.base_dir + "jobs", exist_ok=True)

		# SQLite database
		self.conn = sqlite3.connect(self.base_dir + "jobs.db")
		self.cursor = self.conn.cursor()
		self.cursor.execute('''CREATE TABLE jobs (title TEXT, link TEXT, company_name TEXT, location TEXT, salary TEXT, short_description TEXT, date_posted TEXT, long_description TEXT, date_time_loaded TEXT, full_description_html TEXT)''')

	def get_long_description(self, url):
		self.browser.get(url)
		long_description_element = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "jobDescriptionText")))
		return long_description_element.text

	def get_10_listings(self, url):
		print(url)
		self.browser.get(url)
		with open(f"{self.base_dir}page{self.page_num}.html", "w") as file:
			file.write(self.browser.page_source)
		self.page_num += 1

		jobs = WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jobCard_mainContent")))
		job_instances = []
		for job in jobs:
			try:
				# print(job.get_attribute('innerHTML'))
				
				job_title_element = job.find_element(By.CLASS_NAME, "jobTitle")
				job_title = job_title_element.text #job_title_element.find_element(By.TAG_NAME, "a").get_attribute("title")
				job_title = job.find_element(By.CSS_SELECTOR, "h2.jobTitle a span").get_attribute("title")
				
				job_link = job_title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
				
				company_name = job.find_element(By.CLASS_NAME, "companyName").text
				location = job.find_element(By.CLASS_NAME, "companyLocation").text
				salary_elements = job.find_elements(By.CSS_SELECTOR, ".metadata .attribute_snippet")
				salary = salary_elements[0].text if salary_elements else "Not provided"
				short_description_elements = job.find_elements(By.CSS_SELECTOR, ".job-snippet ul li")
				short_description = " ".join([desc_elem.text for desc_elem in short_description_elements]) if short_description_elements else "Not provided"
				
				date_element = self.browser.find_element(By.CSS_SELECTOR, "span.date")
				date_posted = date_element.text if date_element else "Not provided"
				
				job_instance = Job(job_title, job_link, company_name, location, salary, short_description, date_posted)
				job_instances.append(job_instance)
			except Exception as e:
				print(f"An error occurred: {e}")

		# Check for navigation links and set next_page_available
		nav_element = self.browser.find_element(By.CSS_SELECTOR, "nav[role='navigation']")
		next_page_available = len(nav_element.find_elements(By.CSS_SELECTOR, "a[data-testid='pagination-page-next']")) > 0
		self.next_page_available = next_page_available

		# Get long descriptions
		for job in job_instances:
			print(f"Company:{job.company_name} Title:{job.title}")
			job.long_description = self.get_long_description(job.link)
			company_dir = f"{self.base_dir}jobs/{sanitize_filename(job.company_name)}/"
			os.makedirs(company_dir, exist_ok=True)
			with open(f"{company_dir}{sanitize_filename(job.title)} {datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')}.html", "w") as file:
				file.write(self.browser.page_source)
			self.cursor.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (job.title, job.link, job.company_name, job.location, job.salary, job.short_description, job.date_posted, job.long_description, datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f"), self.browser.page_source))
			self.conn.commit()

		return job_instances

	def get_all_listings(self):
		all_jobs = []
		url = self.base_url
		start_index = 0
		while True:
			jobs = self.get_10_listings(url)
			all_jobs.extend(jobs)
			if not self.next_page_available:
				break
			start_index += 10
			url = f"{self.base_url}&start={start_index}"
			
		return all_jobs

	def close(self):
		self.browser.quit()

# Main function
if __name__ == "__main__":
	scraper = IndeedScraper("Robotics Software Engineer", "Remote")
	all_jobs = scraper.get_all_listings()
	for job in all_jobs:
		print(f"Job Title: {job.title}")
		print(f"Short Description: {job.short_description}")
		# print(f"Long Description: {job.long_description}\n")
	scraper.close()