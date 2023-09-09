from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, aliased
import pandas as pd
from job_questions import *
from JobDatabase import Job, JobSearchFilter

from datetime import datetime, timedelta

# Initialize SQLAlchemy engine and session
JobSearchFilter.add_dynamic_columns(questions)
engine = create_engine("sqlite:///Job_Data/jobs.db")
Session = sessionmaker(bind=engine)
session = Session()

# Step 1: Inner join and Step 2: Filter
JobFilter = aliased(JobSearchFilter)
query = session.query(Job, JobFilter).join(JobFilter, Job.link == JobFilter.job_link).filter(
    and_(
        JobFilter.Degree != 'Yes',
        JobFilter.PLC != 'Yes',
        JobFilter.Education != 'Yes',
        JobFilter.WebDev != 'Yes'
    )
).all()

# Step 3: Load into Pandas DataFrame
data = [{**job.__dict__, **filter_.__dict__} for job, filter_ in query]
df = pd.DataFrame(data)

# Step 4: Calculate actual_date_posted
df['actual_date_posted'] = df['date_time_loaded'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H-%M-%S.%f"))

# Step 5: Sort DataFrame
sort_order = {'Yes': 0, 'No': 1}
sort_columns = ['SmallCompany', 'Entrepreneurial', 'IsDescriptive', 'CompanyDescription', 'Robotics', 'Unity3D', 'MachineLearning', 'EmbeddedSystems', 'actual_date_posted']
df.sort_values(
    by=sort_columns,
    key=lambda col: col.map(sort_order) if col.name != 'actual_date_posted' else col,
    ascending=[True, True, True, True, True, True, True, True, True],
    inplace=True
)

# Step 6: Drop long_description
df.drop(columns=['long_description'], inplace=True)

# Filter out jobs that are too old:
df = df[df['actual_date_posted'] > datetime.now() - timedelta(days=10)]

# order columns:
df = df[['search_term', 'search_location', 'actual_date_posted', 'title', 'company_name', 'salary', 'location', 'Entrepreneurial', 'SmallCompany', 'Robotics', 'Unity3D', 'EmbeddedSystems', 'MachineLearning', 'CompanyDescription', 'IsDescriptive', 'WorkSummary', 'SkillsRequired', 'job_link', 'full_description_html_path']]
df.to_csv('filtered_jobs.csv', index=False)