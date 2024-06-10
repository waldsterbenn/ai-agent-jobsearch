import json
import re
import sys
from bs4 import BeautifulSoup
import requests
import os
import logging
import logging.config
from fake_useragent import UserAgent

# Load the logging configuration
logging.config.fileConfig('logging.config')
log = logging.getLogger('sampleLogger')
ua = UserAgent()

base_folder = "./data/"


def clean_html(html_content):
    # Parse the HTML
    clean = html_content.replace("\n", "").replace("\r", "")
    soup = BeautifulSoup(clean, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # Get text
    text = soup.get_text()

    # Remove any remaining HTML tags
    text = re.sub('<.*?>', '', text)

    # Remove extra whitespace and line breaks
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


url = ""
force_refresh = False

if len(sys.argv) > 1:
    # The first argument after the script name
    url = sys.argv[1]
    if sys.argv[2].lower() == "true":
        force_refresh = True

if (force_refresh == False and os.path.exists(os.path.join(base_folder, "job_contents.json"))):
    log.debug("job_contents.json file already exists. Skipping.")
    exit()

if (force_refresh == False and os.path.exists(os.path.join(base_folder, "html.txt"))):
    log.debug("Loading html from file")
    with open(os.path.join(base_folder, "html.txt"), "r", encoding="utf8") as f:
        content = "\n".join(f.readlines())
else:
    # Make a request to the target URL and get its content:
    log.debug("Downloading html from: "+url)
    headers = {"User-Agent": ua.random}
    response = requests.get(url, headers=headers)
    content = response.text
    with open(os.path.join(base_folder, "html.txt"), "w", encoding="utf8") as f:
        f.write(content)


# Parse the HTML content using BeautifulSoup:

soup = BeautifulSoup(content, "html.parser")

seejob_links = []

# Find all span elements with the "seejobdesktop" class and get their href values:

button_elements = soup.find_all(
    "span", {"class": "btn-list__element d-none d-md-inline"})
seejob_links = [element.find(
    "a", {"class": "btn btn-sm btn-primary seejobdesktop"})["href"] for element in button_elements]

# Fashion forum TODO
# <a href = "https://fashionforum.dk/job/ceo-4/" > </a >
# <a href="https://fashionforum.dk/job/digital-marketing-e-commerce-manager/"></a>
# <a class="newjobs-link" href="https://fashionforum.dk/job/finance-manager-13/"></a>
seejob_links = [element.find(
    "a", {"class": "btn btn-sm btn-primary seejobdesktop"})["href"] for element in button_elements]


# Iterate through the href values and get the HTML contents of each linked page:
output = {}
for link in seejob_links:
    # Generate random user agents for each request to avoid IP block
    link_response = requests.get(link, headers={"User-Agent": ua.random})
    link_content = link_response.text
    clean = clean_html(link_content)
    if len(clean) > 20:
        output[link] = clean
    else:
        log.warning(f"Can't find text for link: {link}")

log.debug(f"Found {len(output)} jobs")

with open(os.path.join(base_folder, "job_contents.json"), "w", encoding="utf8") as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
