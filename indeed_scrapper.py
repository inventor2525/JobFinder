import os
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from Job import Job
	
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
		self.jobs_data_dir = "Job_Data/"
		self.base_dir = f"{self.jobs_data_dir}{sanitize_filename(job)}/{sanitize_filename(location)}/{self.start_time}/"
		os.makedirs(self.base_dir + "jobs", exist_ok=True)

		# SQLite database
		self.conn = sqlite3.connect(self.jobs_data_dir + "jobs.db")
		self.cursor = self.conn.cursor()
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, link TEXT, company_name TEXT, location TEXT, salary TEXT, short_description TEXT, date_posted TEXT, long_description TEXT, date_time_loaded TEXT, full_description_html_path TEXT, search_term TEXT, search_location TEXT)''')
		
		# Load existing jobs into dictionary
		self.jobs_dict = {}
		self.cursor.execute("SELECT * FROM jobs")
		column_names = [description[0] for description in self.cursor.description]
		for row in self.cursor.fetchall():
			link = row[column_names.index('link')]
			job_instance = Job.__new__(Job)
			job_instance.title = row[column_names.index('title')]
			job_instance.link = link
			job_instance.company_name = row[column_names.index('company_name')]
			job_instance.location = row[column_names.index('location')]
			job_instance.salary = row[column_names.index('salary')]
			job_instance.short_description = row[column_names.index('short_description')]
			job_instance.date_posted = row[column_names.index('date_posted')]
			job_instance.long_description = row[column_names.index('long_description')]
			job_instance.date_time_loaded = row[column_names.index('date_time_loaded')]
			job_instance.full_description_html_path = row[column_names.index('full_description_html_path')]
			job_instance.search_term = row[column_names.index('search_term')]
			job_instance.search_location = row[column_names.index('search_location')]
			self.jobs_dict[link] = job_instance
			
	def get_long_description(self, url):
		if url in self.jobs_dict:
			return self.jobs_dict[url].long_description
		self.browser.get(url)
		long_description_element = WebDriverWait(self.browser, 120).until(EC.presence_of_element_located((By.ID, "jobDescriptionText")))
		return long_description_element.text

	def get_10_listings(self, url):
		print(url)
		self.browser.get(url)
		with open(f"{self.base_dir}page{self.page_num}.html", "w") as file:
			file.write(self.browser.page_source)
		self.page_num += 1

		jobs = WebDriverWait(self.browser, 120).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "jobCard_mainContent")))
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
			if job.link not in self.jobs_dict:
				try:
					job.long_description = self.get_long_description(job.link)
					company_dir = f"{self.base_dir}jobs/{sanitize_filename(job.company_name)}/"
					os.makedirs(company_dir, exist_ok=True)
					html_path = f"{company_dir}{sanitize_filename(job.title)} {datetime.now().strftime('%Y-%m-%d %H-%M-%S.%f')}.html"
					with open(html_path, "w") as file:
						file.write(self.browser.page_source)
					self.cursor.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (job.title, job.link, job.company_name, job.location, job.salary, job.short_description, job.date_posted, job.long_description, datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f"), html_path, self.job, self.location))
					self.conn.commit()
					self.jobs_dict[job.link] = job
				except:
					print(f"Error getting job description for link {job.link}")

		return job_instances

	def get_all_listings(self):
		all_jobs = []
		url = self.base_url
		start_index = 0
		while True:
			try:
				jobs = self.get_10_listings(url)
				all_jobs.extend(jobs)
			except:
				print("Error getting 10 listings")
			if not self.next_page_available:
				break
			start_index += 10
			url = f"{self.base_url}&start={start_index}"
			
		return all_jobs

	def close(self):
		self.browser.quit()

# Main function
if __name__ == "__main__":
	def get(role, location):
		scraper = IndeedScraper(role, location)
		all_jobs = scraper.get_all_listings()
		scraper.close()
		return all_jobs
	all_jobs = get("Robotics Software Engineer", "Remote")
	all_jobs = get("Software Engineer", "Remote")
	all_jobs = get("machine learning engineer", "Remote")
	all_jobs = get("game developer", "Remote")
	
	all_jobs = get("Software Engineer", "Grand Rapids Michigan")
	all_jobs = get("Software Engineer", "Kalamazoo Michigan")
	all_jobs = get("Software Engineer", "Holland Michigan")
	
	for job in all_jobs:
		print(f"Job Title: {job.title}")
		print(f"Short Description: {job.short_description}")
		# print(f"Long Description: {job.long_description}\n")