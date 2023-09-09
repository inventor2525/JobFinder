from AbstractAI.ChatBot import *
from AbstractAI.LLMs.OpenAI_LLM import *
from AbstractAI.LLMs.StableBeluga2 import *
from AbstractAI.DB.Database import *

from JobDatabase import JobDatabase, Job, JobSearchFilter, Question

conv_db = Database("sqlite:///job_description_classifications.sql")

model = None
local = False
if local:
	model = StableBeluga2("stabilityai/StableBeluga2")
else:
	model = OpenAI_LLM(model_name="gpt-3.5-turbo")
	
bot = ChatBot(model, conv_db)




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
	Question("WorkSummary", "Work Summary", "A brief summary of the kind of work this job might entail", "Summary"),
	Question("SkillsRequired", "Skills Required", "A list of the skills required for this job, in order of importance.", "List of skills, comma separated")
]

longs = "\n".join([f"{i+1}. {q.long_description}" for i,q in enumerate(questions)])
shorts = "\n".join([f"{q.short_description}: [{q.answer_format}]" for i,q in enumerate(questions)])
system_message = Message(
		f"""You are an automated job description quality checker. It is very important that you respond in a certain format so that your response can be parsed automatically to sort job descriptions programmatically. You will be given a copy of a job description, you must then look in the job description for several key things. Look for the following things:

{longs}

respond with the following format:
{shorts}""",
	Role.System, source=UserSource("System")
)

print(system_message.content)

def new_conversation():
	bot.conversation = Conversation()
	bot.conversation.add_message(message=system_message)

#load resume:
resume = open("resume.txt", "r").read()



i = 0
JobSearchFilter.add_dynamic_columns(questions)
db = JobDatabase("sqlite:///Job_Data/jobs.db")
done_jobs = set([j.job_link for j in db.get_jobs_with_conversations()])

for job in db.get_all_jobs():
	if job.link in done_jobs:
		continue
	new_conversation()
	job_info = bot.prompt(f"Heres a job description:\n{job.long_description}")
	
	thing = db.insert_responses(bot.conversation.hash, job.link, questions, job_info)
	i += 1
	print(f"================{i}")
	print(job.title)
	print(job.company_name)
	print(job.link)
	print(job_info)
	print("================")