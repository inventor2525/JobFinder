from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
import pandas as pd
from job_questions import *
from JobDatabase import Job, JobSearchFilter

# Initialize SQLAlchemy engine and session
JobSearchFilter.add_dynamic_columns(questions)
engine = create_engine("sqlite:///Job_Data/jobs.db")
Session = sessionmaker(bind=engine)
session = Session()

# Step 1: Filter tables
filtered_jobs = session.query(Job).all()
filtered_filters = session.query(JobSearchFilter).filter(
    and_(
        JobSearchFilter.Degree != 'Yes',
        JobSearchFilter.PLC != 'Yes',
        JobSearchFilter.WebDev != 'Yes'
    )
).all()

# Step 2: Inner join tables
joined_data = []
for job in filtered_jobs:
    for filter_ in filtered_filters:
        if job.link == filter_.job_link:
            row = {
                'actual_date_posted': job.actual_date_posted,
                'SmallCompany': filter_.SmallCompany,
                'Entrepreneurial': filter_.Entrepreneurial,
                'IsDescriptive': filter_.IsDescriptive,
                'CompanyDescription': filter_.CompanyDescription,
                'Robotics': filter_.Robotics,
                'Unity3D': filter_.Unity3D
            }
            joined_data.append(row)

# Step 3: Load into Pandas DataFrame
df = pd.DataFrame(joined_data)

# Step 4: Sort DataFrame
sort_order = {
    'Yes': 0,
    'No': 1
}

sort_columns = ['SmallCompany', 'Entrepreneurial', 'IsDescriptive', 'CompanyDescription', 'Robotics', 'Unity3D', 'actual_date_posted']
df.sort_values(
    by=sort_columns,
    key=lambda col: col.map(sort_order) if col.name != 'actual_date_posted' else col,
    ascending=[True, True, True, True, True, True, True],
    inplace=True
)

# Step 5: Return sorted DataFrame
print(df)

# Step 6: Save to CSV
df.to_csv('filtered_jobs.csv', index=False)