from AbstractAI.ChatBot import *
from AbstractAI.LLMs.OpenAI_LLM import *
from AbstractAI.LLMs.StableBeluga2 import *
from AbstractAI.DB.Database import *

from job_questions import *
from JobDatabase import JobDatabase, Job, JobSearchFilter

conv_db = Database("sqlite:///job_description_classifications.sql")

model = None
model2 = None
local = False
if local:
	model = StableBeluga2("stabilityai/StableBeluga2")
else:
	model = OpenAI_LLM(model_name="gpt-3.5-turbo")
	model2 = OpenAI_LLM(model_name="gpt-3.5-turbo-16k")
	
bot = ChatBot(model, conv_db, fallback_model=model2)

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