from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

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

		return session.query(Job).all()

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