from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, aliased
import pandas as pd
from job_questions import *
from JobDatabase import Job, JobSearchFilter, JobNotes, Base

from datetime import datetime, timedelta

# Initialize SQLAlchemy engine and session
JobSearchFilter.add_dynamic_columns(questions)
engine = create_engine("sqlite:///Job_Data/jobs.db")
Base.metadata.create_all(engine)
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


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QTextEdit, QPushButton, QSpinBox, QScrollArea, QFrame
from sqlalchemy.orm.exc import NoResultFound
import sys

class JobRatingWindow(QWidget):
	def __init__(self, df, session, start_index=0):
		super().__init__()
		self.df = df
		self.session = session
		self.current_index = start_index
		self.initUI()

	def load_job_data(self):
		self.job_data = self.df.iloc[self.current_index]
		self.job_title_company.setText(f"{self.job_data['title']} at {self.job_data['company_name']}")
		self.job_date_salary.setText(f"Posted: {self.job_data['actual_date_posted']} | Salary: {self.job_data['salary']}")
		self.job_term_location.setText(f"Search Term: {self.job_data['search_term']} | Location: {self.job_data['search_location']}")
		self.long_description.setText(self.job_data['long_description'])
		
		# Load existing notes from the database
		existing_note = self.session.query(JobNotes).filter_by(job_link=self.job_data['job_link']).first()
		if existing_note:
			self.star_rating.setValue(existing_note.star_rating)
			self.go_no_go.setChecked(existing_note.go_no_go)
			self.notes.setText(existing_note.notes)
			self.no_go_reason.setText(existing_note.no_go_reason if existing_note.no_go_reason else "")
		else:
			self.star_rating.setValue(1)
			self.go_no_go.setChecked(False)
			self.notes.clear()
			self.no_go_reason.clear()

	def initUI(self):
		layout = QVBoxLayout()

		# Checkbox for filtering already rated jobs
		self.filter_checkbox = QCheckBox('Only show unrated jobs')
		layout.addWidget(self.filter_checkbox)

		# Job information
		self.job_info_layout = QVBoxLayout()
		self.job_title_company = QLabel()
		self.job_date_salary = QLabel()
		self.job_term_location = QLabel()
		self.job_info_layout.addWidget(self.job_title_company)
		self.job_info_layout.addWidget(self.job_date_salary)
		self.job_info_layout.addWidget(self.job_term_location)

		# Scrollable long description
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		frame = QFrame(scroll)
		scroll.setWidget(frame)
		scroll_layout = QVBoxLayout(frame)
		self.long_description = QLabel()
		self.long_description.setWordWrap(True)
		scroll_layout.addWidget(self.long_description)

		self.job_info_layout.addWidget(scroll)
		layout.addLayout(self.job_info_layout)

		# Job notes section
		self.notes_layout = QVBoxLayout()
		self.star_rating = QSpinBox()
		self.star_rating.setRange(1, 5)
		self.go_no_go = QCheckBox('Go/No-Go')
		self.notes = QTextEdit()
		self.no_go_reason = QTextEdit()
		self.no_go_reason.setVisible(False)
		self.confirm_button = QPushButton('Confirm')
		self.next_button = QPushButton('Next')
		self.prev_button = QPushButton('Previous')

		button_layout = QHBoxLayout()
		button_layout.addWidget(self.prev_button)
		button_layout.addWidget(self.next_button)
		button_layout.addWidget(self.confirm_button)

		self.notes_layout.addWidget(self.star_rating)
		self.notes_layout.addWidget(self.go_no_go)
		self.notes_group = QHBoxLayout()
		self.notes_group.addWidget(self.notes)
		self.notes_group.addWidget(self.no_go_reason)
		self.notes_layout.addLayout(self.notes_group)
		self.notes_layout.addLayout(button_layout)

		layout.addLayout(self.notes_layout)

		# Connect signals
		self.go_no_go.toggled.connect(self.no_go_reason.setVisible)
		self.confirm_button.clicked.connect(self.save_notes)
		self.next_button.clicked.connect(self.next_job)
		self.prev_button.clicked.connect(self.prev_job)

		self.setLayout(layout)
		self.load_job_data()
		self.show()

	def save_notes(self):
		existing_note = self.session.query(JobNotes).filter_by(job_link=self.job_data['job_link']).first()
		if existing_note:
			existing_note.star_rating = self.star_rating.value()
			existing_note.go_no_go = self.go_no_go.isChecked()
			existing_note.notes = self.notes.toPlainText()
			existing_note.no_go_reason = self.no_go_reason.toPlainText() if self.go_no_go.isChecked() else None
		else:
			job_note = JobNotes(
				job_link=self.job_data['job_link'],
				star_rating=self.star_rating.value(),
				go_no_go=self.go_no_go.isChecked(),
				notes=self.notes.toPlainText(),
				no_go_reason=self.no_go_reason.toPlainText() if self.go_no_go.isChecked() else None
			)
			self.session.add(job_note)
		self.session.commit()

	def next_job(self):
		if self.current_index < len(self.df) - 1:
			self.current_index += 1
			self.load_job_data()

	def prev_job(self):
		if self.current_index > 0:
			self.current_index -= 1
			self.load_job_data()

# Initialize the PyQt application
app = QApplication(sys.argv)
window = JobRatingWindow(df, session)
sys.exit(app.exec_())