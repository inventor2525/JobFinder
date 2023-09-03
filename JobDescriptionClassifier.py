from AbstractAI.ChatBot import *
from AbstractAI.LLMs.OpenAI_LLM import *
from AbstractAI.LLMs.StableBeluga2 import *
from AbstractAI.DB.Database import *

conv_db = Database("sqlite:///job_description_classifications.sql")

model = None
local = False
if local:
	model = StableBeluga2()
else:
	model = OpenAI_LLM(model_name="gpt-3.5-turbo-16k")
	
bot = ChatBot(model, conv_db)

system_message = Message(
		r"""You are an automated job description quality checker. It is very important that you respond in a certain format so that your response can be parsed automatically to sort job descriptions programmatically. You will be given a copy of the user's resume and a job description. You must then look in the job description for several key things and rate the job based on the user's experience. Look for the following things:

1. If any form of education preference is mentioned in the job description.
2. If there is a hard requirement for a degree mentioned in the job description.3. If the job mentions any skills not listed in the resume.
4. On a scale of 1-10, how well does the user's experience match the job description?
5. On a scale of 1-10, how much of the users experience will be effectively utilized in this job?
6. On a scale of 1-10, how much the user might enjoy this job.

respond with the following format:
Education Preference: [Yes/No]
Degree Required: [Yes/No]
Skills Not Listed: [List of skills]
Experience Match: [1-10]
Experience Utilization: [1-10]
Job Enjoyment: [1-10]

Here is an example conversation for you to go by, please respond as such:
User:
Here is a copy of my resume and the job description.

Assistant:
Education Preference: Yes
Degree Required: No
Skills Not Listed: [Java]
Experience Match: 8
Experience Utilization: 3
Job Enjoyment: 7""",
	Role.System, source=UserSource("System")
)

def new_conversation():
	bot.conversation = Conversation()
	bot.conversation.add_message(message=system_message)

#load resume:
resume = open("resume.txt", "r").read()

from JobDatabase import JobDatabase, Job

db = JobDatabase("sqlite:///Job_Data/jobs.db")
for job in db.get_all_jobs()[10:]:
	new_conversation()
	job_info = bot.prompt(f"Heres a copy of my resume:\n{resume}\n========\n========\nAnd here is the job description:\n{job.long_description}")
	print(job_info)
	
	input("Press enter to continue...")