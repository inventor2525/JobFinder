from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, aliased
import pandas as pd
from job_questions import *
from JobDatabase import Job, JobSearchFilter, JobNotes

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
# df.drop(columns=['long_description'], inplace=True)

# Filter out jobs that are too old:
df = df[df['actual_date_posted'] > datetime.now() - timedelta(days=10)]

# order columns:
df = df[['search_term', 'search_location', 'actual_date_posted', 'title', 'company_name', 'salary', 'location', 'Entrepreneurial', 'SmallCompany', 'Robotics', 'Unity3D', 'EmbeddedSystems', 'MachineLearning', 'CompanyDescription', 'IsDescriptive', 'WorkSummary', 'SkillsRequired', 'job_link', 'full_description_html_path', 'long_description']]
df.to_csv('filtered_jobs.csv', index=False)


from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QTextEdit, QPushButton, QSpinBox, QScrollArea, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
import sys

class JobRatingWindow(QWidget):
	def __init__(self, job_data, session):
		super().__init__()
		self.job_data = job_data
		self.session = session
		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		# Checkbox for filtering already rated jobs
		self.filter_checkbox = QCheckBox('Only show unrated jobs')
		layout.addWidget(self.filter_checkbox)

		# Job information
		job_info_layout = QVBoxLayout()
		job_title_company = QLabel(f"{self.job_data['title']} at {self.job_data['company_name']}")
		job_date_salary = QLabel(f"Posted: {self.job_data['actual_date_posted']} | Salary: {self.job_data['salary']}")
		job_term_location = QLabel(f"Search Term: {self.job_data['search_term']} | Location: {self.job_data['search_location']}")
		job_info_layout.addWidget(job_title_company)
		job_info_layout.addWidget(job_date_salary)
		job_info_layout.addWidget(job_term_location)

		# Scrollable long description
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		frame = QFrame(scroll)
		scroll.setWidget(frame)
		scroll_layout = QVBoxLayout(frame)
		long_description = QLabel(self.job_data['long_description'])
		long_description.setWordWrap(True)
		scroll_layout.addWidget(long_description)

		job_info_layout.addWidget(scroll)
		layout.addLayout(job_info_layout)

		# Job notes section
		notes_layout = QVBoxLayout()
		self.star_rating = QSpinBox()
		self.star_rating.setRange(1, 5)
		self.go_no_go = QCheckBox('Go/No-Go')
		self.notes = QTextEdit()
		self.no_go_reason = QTextEdit()
		self.no_go_reason.setVisible(False)
		self.confirm_button = QPushButton('Confirm')

		notes_layout.addWidget(self.star_rating)
		notes_layout.addWidget(self.go_no_go)
		notes_layout.addWidget(self.notes)
		notes_layout.addWidget(self.no_go_reason)
		notes_layout.addWidget(self.confirm_button)

		layout.addLayout(notes_layout)

		# Connect signals
		self.go_no_go.toggled.connect(self.no_go_reason.setVisible)
		self.confirm_button.clicked.connect(self.save_notes)

		self.setLayout(layout)
		self.show()

	def save_notes(self):
		# Save the notes to the database
		job_note = JobNotes(
			job_link=self.job_data['job_link'],
			star_rating=self.star_rating.value(),
			go_no_go=self.go_no_go.isChecked(),
			notes=self.notes.toPlainText(),
			no_go_reason=self.no_go_reason.toPlainText() if self.go_no_go.isChecked() else None
		)
		self.session.add(job_note)
		self.session.commit()

# Initialize the PyQt application
app = QApplication(sys.argv)

# Iterate through the jobs in the Pandas DataFrame
for index, row in df.iterrows():
	window = JobRatingWindow(row, session)
	sys.exit(app.exec_())
