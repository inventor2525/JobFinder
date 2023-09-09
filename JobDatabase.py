from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from typing import List
import regex as re

from datetime import datetime, timedelta

Base = declarative_base()

class Question:
	def __init__(self, column_name:str, short_description:str, long_description:str, answer_format:str):
		self.column_name = column_name
		self.short_description = short_description
		self.long_description = long_description
		self.answer_format = answer_format
		
class Job(Base):
	__tablename__ = 'jobs'

	id = Column(Integer, primary_key=True)
	title = Column(String)
	link = Column(String)
	company_name = Column(String)
	location = Column(String)
	salary = Column(String)
	short_description = Column(String)
	date_posted = Column(String)
	long_description = Column(String)
	date_time_loaded = Column(String)
	full_description_html_path = Column(String)
	search_term = Column(String)
	search_location = Column(String)
	
	@property
	def actual_date_posted(self):
		# Parse date_time_loaded to datetime object
		date_time_loaded = datetime.strptime(self.date_time_loaded, "%Y-%m-%d %H-%M-%S.%f")
		
		# Regular expression patterns for different formats
		patterns = [
			("Active (\d+) days ago", timedelta(days=-1)),
			("Posted (\d+)\+? days ago", timedelta(days=-1)),
			("Just posted", timedelta(days=0)),
			("Today", timedelta(days=0))
		]
		
		for pattern, delta in patterns:
			match = re.search(pattern, self.date_posted)
			if match:
				if delta.days == -1:
					days_ago = int(match.group(1))
					return date_time_loaded + timedelta(days=-days_ago)
				else:
					return date_time_loaded + delta
		return date_time_loaded
	
class JobSearchFilter(Base):
	__tablename__ = 'job_search_filter'

	id = Column(Integer, primary_key=True)
	job_link = Column(String, ForeignKey('jobs.link'))
	conversation_hash = Column(String)
	# Columns will be added dynamically
	
	@classmethod
	def add_dynamic_columns(cls, questions: List[Question]):
		for q in questions:
			setattr(cls, q.column_name, Column(Text))
	
class JobDatabase:
	def __init__(self, db_url="sqlite:///Job_Data/jobs.db"):
		self.engine = create_engine(db_url)
		self.create_jobs_table()

	def create_jobs_table(self):
		Base.metadata.create_all(self.engine)

	def add_job(self, job):
		Session = sessionmaker(bind=self.engine)
		session = Session()

		session.add(job)
		session.commit()

	def get_all_jobs(self):
		Session = sessionmaker(bind=self.engine)
		session = Session()

		jobs = session.query(Job).all()
		return sorted(jobs, key=lambda job: job.actual_date_posted, reverse=True)
	
	def get_jobs_with_conversations(self):
		Session = sessionmaker(bind=self.engine)
		session = Session()

		return session.query(JobSearchFilter).all()
	
	def insert_responses(self, conversation_hash, job_link, questions, llm_response):
		Session = sessionmaker(bind=self.engine)
		session = Session()
		new_entry = JobSearchFilter()
		new_entry.conversation_hash = conversation_hash
		new_entry.job_link = job_link

		for i in range(len(questions) - 1):
			pattern = re.compile(f"{questions[i].short_description}: (.*?)\n{questions[i+1].short_description}:", re.DOTALL)
			match = pattern.search(llm_response)
			if match:
				setattr(new_entry, questions[i].column_name, match.group(1).strip())

		# For the last question
		pattern = re.compile(f"{questions[-1].short_description}: (.*)", re.DOTALL)
		match = pattern.search(llm_response)
		if match:
			setattr(new_entry, questions[-1].column_name, match.group(1).strip())

		session.add(new_entry)
		session.commit()
		return new_entry
		
if __name__ == "__main__":
	job_db = JobDatabase()
	
	for job in job_db.get_all_jobs():
		print(f"Company: {job.company_name} | Title: {job.title} \n Salary: {job.salary} | Location: {job.location} \n Short Description: {job.short_description} \n Date Posted: {job.date_posted}")
		print(f"Long Description:\n{job.long_description}")
		print(f"=============")
		print(f"=============")
		print(f"=============")
		print(f"=============")
		print(f"=============")