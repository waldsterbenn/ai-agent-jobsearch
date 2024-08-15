
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
current_model = "llama3:8b-instruct-q8_0"
current_model = "llama3.1"

llm_model_id = "cognitivecomputations/dolphin-2.7-mixtral-8x7b"
llm_model_id = "microsoft/WizardLM-2-7B"
llm_model_id = "llama3:8b-instruct-q8_0"
llm_model_id = "llama3.1"

base_folder = "./data/"

fmt = "%Y-%m-%d"
output_file = f"{time.strftime(fmt, time.gmtime())}-job-report.md"
with open(os.path.join(base_folder, output_file), 'r', encoding="utf8") as f:
    data = f.readlines()

ollama_client = OpenAI(base_url="http://localhost:11434/v1",
                       api_key="ollama")

user_prompt = f"""
        <job_report>
            {data}
        </job_report>
        
        Above is a report in Markdown format, found between the 'job_report' tags.
        Condense the information into an e-mail, as a headhunter would send to a client.
        You keep no secrets and hold no information back.
        Focus on the top pick for the candidate. But also brifly mention the other jobs that could be of interrest to the client.
        Think carefully before writing the e-mail and make sure you do not add information that is not based on the 'rob_report' data.
        Only give me the e-mail text.
        
        PLEASE NOTE: DO NOT ADD ANY EXTRA TEXT, COMMENTS OR OPPINIONS TO THE OUTPUT.
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
    temperature=0.5,
    # max_tokens=5000,
    stream=False,
)
summarytext = ollama_completion.choices[0].message.content

with open(os.path.join(base_folder, "email.txt"), 'w', encoding="utf8") as file:
    file.write(summarytext)
