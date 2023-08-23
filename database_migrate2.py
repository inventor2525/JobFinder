import os
import sqlite3
import glob

def update_html_paths():
	# Connect to the new database
	new_conn = sqlite3.connect("Job_Data/jobs.db")
	new_cursor = new_conn.cursor()

	# Select all rows from the new database
	new_cursor.execute("SELECT rowid, company_name, title, full_description_html_path, search_term, search_location FROM jobs")
	rows = new_cursor.fetchall()

	# Directory structure
	base_dir = "Job_Data_OLD/"

	for row in rows:
		rowid, company_name, title, html_path, search_term, search_location = row
		job_dir = os.path.join(base_dir, sanitize_filename(search_term), sanitize_filename(search_location))

		# Look for HTML files
		pattern = os.path.join(job_dir, "*", "jobs", sanitize_filename(company_name), sanitize_filename(title)) +  "*.html"
		html_files = glob.glob(pattern)
		
		if len(html_files) > 1:
			print(f"{pattern}\n{html_files}\n\n")
		if len(html_files) == 0:
			print(f"{rowid} {pattern}")
			
		# Validate the HTML content and update the path if a match is found
		found_match = False
		for html_file in html_files:
			with open(html_file, 'r') as file:
				file_content = file.read()
				if file_content == html_path: # Compare with the HTML content in the database
					new_cursor.execute("UPDATE jobs SET full_description_html_path = ? WHERE rowid = ?", (html_file, rowid))
					new_conn.commit()
					found_match = True
					break

		# if not found_match:
		# 	print(f"Could not find file for row index {rowid}, company {company_name}, title {title}")

	new_conn.close()

def sanitize_filename(filename):
	return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

if __name__ == "__main__":
	update_html_paths()
