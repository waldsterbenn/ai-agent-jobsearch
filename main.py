import os
import shutil
import subprocess
import logging
import logging.config
import time

# Load the logging configuration
logging.config.fileConfig('logging.config')
logger = logging.getLogger('sampleLogger')


def run_script(script_path, args=None):
    if args is None:
        args = []
    try:
        # Command includes the script path and any arguments
        command = ['python', script_path] + args
        # Run the script
        subprocess.run(command, check=True,
                       text=True, capture_output=True)
        logger.info(f"Script {script_path} finished successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Script {script_path} failed.")
        logger.exception("Error:", e.stderr)


base_folder = "./data/"
if not os.path.exists(base_folder):
    os.mkdir(base_folder)

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

urls = {
    "Jobindex": "https://www.jobindex.dk/jobsoegning/it/systemudvikling/region-midtjylland",
    "Jobfinder": "https://www.jobfinder.dk/jobs?keywords=&radius=-&latlon=Aarhus%2C%20Danmark",
}

url = urls["Jobindex"]
force_refresh = True
force_refresh = False

run_script("job_scraper.py", [url, str(force_refresh)])
run_script("llm_analyse_jobs.py", [str(force_refresh)])
run_script("report_generator.py", [user_cv])
# run_script("email_report_generator.py")

# Copy files to obsidian
fmt = "%Y-%m-%d"
date = f"{time.strftime(fmt, time.gmtime())}"
report_file = os.path.join(base_folder, f"{date}-job-report.md")

new_folder = os.path.join(
    "C:\\Users\\ls\\Documents\\Obsidian\\Noter\\Coding\\AI jobsøgning", date)
if not os.path.exists(new_folder):
    os.mkdir(new_folder)

destination_file = os.path.join(new_folder, "job report.md")

shutil.copy(report_file, destination_file)
logger.info(f"Copied files to Obsidian at: {destination_file}")

email_file = os.path.join(base_folder, f"email.txt")

destination_file = os.path.join(new_folder, f"email.md")

shutil.copy(email_file, destination_file)
