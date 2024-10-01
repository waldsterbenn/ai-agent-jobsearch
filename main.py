import os
import shutil
import subprocess
import logging
import logging.config
import time

# Load the logging configuration
logging.config.fileConfig('logging.config')
logger = logging.getLogger('sampleLogger')

urls = {
    "Jobindex": "https://www.jobindex.dk/jobsoegning/it/systemudvikling/region-midtjylland",
    "Jobfinder": "https://www.jobfinder.dk/jobs?keywords=&radius=-&latlon=Aarhus%2C%20Danmark",
}

url = urls["Jobindex"]

# configure if you want to force a refresh
force_refresh = False
force_refresh = True


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

try:
    with open("./user_cv.txt") as f:
        user_cv = f.readlines()[0].strip()
except FileNotFoundError:
    logger.error("No cv file found.")
    exit(1)
if not user_cv:
    user_cv = "This candidate has qualifications"

run_script("job_scraper.py", [url, str(force_refresh)])
run_script("llm_analyse_jobs.py", [str(force_refresh)])
run_script("report_generator.py", [user_cv])
run_script("email_report_generator.py")

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
