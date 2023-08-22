import os
import sqlite3
import glob

def sanitize_filename(filename):
	return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

def import_previous_databases():
	# Connect to the new database
	new_conn = sqlite3.connect("Job_Data/jobs.db")
	new_cursor = new_conn.cursor()
	new_cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (title TEXT, link TEXT, company_name TEXT, location TEXT, salary TEXT, short_description TEXT, date_posted TEXT, long_description TEXT, date_time_loaded TEXT, full_description_html_path TEXT, search_term TEXT, search_location TEXT)''')

	# Directory structure
	base_dir = "Job_Data_OLD/"
	
	# Iterate through the existing directories
	for job_folder in os.listdir(base_dir):
		job = sanitize_filename(job_folder)
		for location_folder in os.listdir(os.path.join(base_dir, job_folder)):
			location = sanitize_filename(location_folder)
			for date_folder in os.listdir(os.path.join(base_dir, job_folder, location_folder)):
				db_path = os.path.join(base_dir, job_folder, location_folder, date_folder, "jobs.db")
				if os.path.exists(db_path):
					# Connect to the old database
					old_conn = sqlite3.connect(db_path)
					old_cursor = old_conn.cursor()
					old_cursor.execute("SELECT * FROM jobs")
					for row in old_cursor.fetchall():
						# Append search term and location to the existing data
						new_row = row + (job, location)
						print(new_row)
						new_cursor.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", new_row)
						new_conn.commit()
					old_conn.close()

	new_conn.close()

if __name__ == "__main__":
	import_previous_databases()
