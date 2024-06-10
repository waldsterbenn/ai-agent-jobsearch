import sys
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
current_model = "phi3:14b"

llm_model_id = "cognitivecomputations/dolphin-2.7-mixtral-8x7b"
llm_model_id = "microsoft/WizardLM-2-7B"
llm_model_id = "llama3:8b-instruct-q8_0"
llm_model_id = "phi3:14b"

base_folder = "./data/"

force_refresh = False

if len(sys.argv) > 1:
    # The first argument after the script name
    if sys.argv[1].lower() == "true":
        force_refresh = True

if (force_refresh == False and os.path.exists(os.path.join(base_folder, "job_summaries.json"))):
    logger.debug("job_summaries.json file already exists. Skipping.")
    exit()

with open(os.path.join(base_folder, "job_contents.json"), "r", encoding="utf8") as f:
    data = f.readlines()
    data = ''.join(data)
    jobs_html = json.loads(data)

ollama_client = OpenAI(base_url="http://localhost:11434/v1",
                       api_key="ollama")

element_count = len(jobs_html.items())
logger.debug(f"Processing {element_count} jobs")

tokenizer = None
try:
    tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
except OSError as e:
    logger.error(e)

counter = 0
summaries = {}
for key, value in jobs_html.items():
    counter = counter+1
    logger.debug(f"Processing {counter}/{element_count}: {key}")
    if value == "" or len(value) < 20:
        continue
# Take your time and analyse the text carefully before coming with a response.
    user_prompt = f"""
        You are an analytical bot, that only respond with data output. Ouput that's clean and easy to read.
        You are provided with a job post from a website, contained in the 'job text' section.
        If needed, translate it to english.
                
        Job text:
        ---
            {value}
        ---
        End of job text.
        
        Instructions:
        You will make a summary of the text, where you focus on the job content and required competencies like skills and technologies. 
        Ignore info about the company and other such filler info.
        Make sure to put in the company name, as the first thing in the summary.
        The summary should be in Markdown format (as described on https://www.markdownguide.org), exactly as shown in the example below.
        
        Example layout:
        ### Company Name
        ### Summary
        ### Competencies
        ### Technologies
        ### Other
    """

    chat = [
        # {"role": "system", "content": system_prompt},
        # {"role": "assistant", "content": "Sure, i will follow your instructions, stick to the dataset and not make up new data."},
        {"role": "user", "content": user_prompt},
    ]

    if tokenizer is None:
        templated_prompt = f"{user_prompt}"
    else:
        templated_prompt = tokenizer.apply_chat_template(
            chat, tokenize=False, add_generation_prompt=True)

    ollama_completion = ollama_client.chat.completions.create(
        messages=[{
            'role': 'user',
            'content': templated_prompt
        }],
        model=current_model,
        temperature=0.3,
        max_tokens=500,
        stream=False,
    )
    summarytext = ollama_completion.choices[0].message.content

    summaries[f"{key}"] = summarytext

logger.debug(f"Processed {element_count} jobs")
# Correctly write the JSON data to a file
with open(os.path.join(base_folder, "job_summaries.json"), "w", encoding="utf8") as f:
    json.dump(summaries, f, ensure_ascii=False, indent=4)
