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