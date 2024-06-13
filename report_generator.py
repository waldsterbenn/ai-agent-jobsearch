
import sys
import time
from transformers import AutoTokenizer
from openai import OpenAI
import json
import logging
import logging.config
import os

# Load the logging configuration
logging.config.fileConfig('logging.config')
logger = logging.getLogger('sampleLogger')

current_model = "mixtral"
current_model = "wizardlm2:7b"
current_model = "phi3:14b"
current_model = "llama3:8b-instruct-q8_0"

llm_model_id = "cognitivecomputations/dolphin-2.7-mixtral-8x7b"
llm_model_id = "microsoft/WizardLM-2-7B"
llm_model_id = "phi3:14b"
llm_model_id = "llama3:8b-instruct-q8_0"

base_folder = "./data/"

# Just mash your linked-in about section into this variable
user_cv = """
        Senior Software Developer | Software/System Engineer | AI and Machine Learning Enthusiast | Crafty software builder

        I want to build systems that move things forward. Massive legacy systems that maintain the status quo, is not my thing. Let's build something new instead.

        Self taught in machine learning subjects. Have been diving into building Agentic systems, speech and text processing, RAG backed bots and other fun stuff.
        Experience with building sw using OpenAi and open source local LLMs.
        Mistral, Mixtral, LLAMA, StarCoder, Whisper etc.

        About me:
        - A pragmatic and generalist that gets things done. 
        - I like to analyze and build new things. 
        - Comfortable working independently or in teams.
        - Proficient in SW architecture and design.
        - I like a little structure, but rely on my own judgment.
        - Memorization is not my thing, but creativity is.
        - I emphasize on building aesthetic and quality software.

        Proficient with a broad variety of tech and tools like:
        C#, processing pipelines and message bus, WPF, SQL, JS, React, Node, Electron, Java, Python.
        AWS, Docker, Gradle, Maven, AzureDevops/VSOnline, vector databases.

        Looking for roles where creativity drives progress and innovation is the goal.
    """

if len(sys.argv) > 1:
    # The first argument after the script name
    user_cv = sys.argv[1]

with open(os.path.join(base_folder, "job_summaries.json"), "r", encoding="utf8") as f:
    data = f.readlines()
    data = ''.join(data)
    jobs_html = json.loads(data)

ollama_client = OpenAI(base_url="http://localhost:11434/v1",
                       api_key="ollama")
user_prompt = f"""
        Jobs data:
        ---
            {data}
        ---
        End of jobs data.

        Client's linkedin profile:
        ---
            {user_cv}
        ---
        End of linkedin profile.
        
        You are a skilled headhunter who helps clients find new jobs. You keep no secrets and hold no information back from you're client.
        You're client is a competent professional, looking for new oppotunities in the job market.
        Use information from client's 'linkedin profile', when analysing the best fit.
        You're task is to analyse the information about the {len(jobs_html)} currently available jobs, found in the 'jobs data' section.
        You have to find the most suitable position for the client. If there are no good match that's also ok.
        With you'r knowledge about the client, pick one of the job offers - as the top pick, and motivate why you think it's the best choice.
    """

messages = [
    {"role": "user", "content": user_prompt},
]


tokenizer = None
try:
    tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
except OSError as e:
    logger.error(e)

if tokenizer is None:
    templated_prompt = f"USER: {user_prompt}"
else:
    templated_prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True)

logger.debug(f"Generating report with LLM: \n{templated_prompt}")

ollama_completion = ollama_client.chat.completions.create(
    messages=[{
        'role': 'user',
        'content': templated_prompt
    }],
    model=current_model,
    temperature=0.3,
    max_tokens=1000,
    stream=False,
)
summarytext = ollama_completion.choices[0].message.content
fmt = "%Y-%m-%d"
output_file = f"{time.strftime(fmt, time.gmtime())}-job-report.md"
counter = 0
# Writing data to markdown file
with open(os.path.join(base_folder, output_file), 'w', encoding="utf8") as file:
    file.write(f"# Top pick\n{summarytext}\n")
    file.write(f"---\n")
    file.write(f"# All Jobs\n")
    for url, description in jobs_html.items():
        counter = counter+1
        file.write(f"## Job {counter}\n")
        file.write(f"[Link]({url})\n")
        file.write(f"{description}\n\n")
