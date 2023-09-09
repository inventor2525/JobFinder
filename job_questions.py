from JobDatabase import Question

questions = [
	Question("Education", "Education Preference", "Is there any form of preference for education is mentioned in the job description. For example if any of these things are mentioned, masters, bachelors. doctorate, ms, bs, phd, degree, education, etc. Even if they say 'or equivalent experience', then 'education' is mentioned.", "Yes/No"),
	Question("Degree", "Degree Required", "If there is a hard requirement for a degree mentioned in the job description, eg, if you MUST have a degree and there is no mention of 'or equiv experience'.", "Yes/No"),
	Question("WebDev", "Web development Mentioned", "If the job mentions anything to do with web development.", "Yes/No"),
	Question("PLC", "PLCs mentioned", "If the job mentions anything to do with plc's", "Yes/No"),
	Question("Unity3D", "Unity3D mentioned", "Does the job mention Unity3D or game development in any capacity", "Yes/No"),
	Question("Robotics", "Robotics mentioned", "Does the job mention robotics in any capacity", "Yes/No"),
	Question("EmbeddedSystems", "Embedded Systems mentioned", "Does the job mention embedded systems in any capacity", "Yes/No"),
	Question("MachineLearning", "Machine Learning mentioned", "Does the job mention machine learning in any capacity", "Yes/No"),
	Question("Entrepreneurial", "Entrepreneurial Mindset", "Does the job mention any sort of need or desire for a entrepreneurial or cross disciplinary mind set", "Yes/No"),
	Question("SmallCompany", "Small Company/Startup", "Is there any mention of this being for a small company or startup", "Yes/No"),
	Question("CompanyDescription", "Company Description", "Does the job description mention anything about the company and what they do", "Yes/No"),
	Question("IsDescriptive", "Descriptive", "Is the job description descriptive (containing long paragraphs of text) rather than just being a list of requirements", "Yes/No"),
	Question("WorkSummary", "Work Summary", "A brief summary of the kind of work this job might entail", "Summary"),
	Question("SkillsRequired", "Skills Required", "A list of the skills required for this job, in order of importance.", "List of skills, comma separated")
]