from bs4 import BeautifulSoup
import requests, json, time
from openai import OpenAI

#ADD YOUR PRODUCT URL
site = "PRODUCT-URL"

headers = {"User-Agent":"Mozilla/5.0"}

r = requests.get(site,headers=headers)

soup = BeautifulSoup(r.content,'html.parser')

page_title = soup.title.text.strip()
page_title = page_title.replace("\n"," ")
page_h1 = soup.h1.text.strip()


webpage_content = soup.find_all("p")
parsed_content = []

for c in webpage_content:
    content = c.text
    content = content.replace("\n"," ").strip()
    parsed_content.append(content)

content = ""

for pc in parsed_content:
    content += pc

assistant_content = page_title + " " + page_h1 + " " + content

# OpenAI Begins
creds = 'creds.json'

with open(creds) as f:
    creds = json.load(f)

assistant = creds['assistant']

client = OpenAI(api_key=creds['secret'],organization=creds['org'])

def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(assistant, thread, user_input)
    return thread, run

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

thread, run = create_thread_and_run(content)
run = wait_on_run(run, thread)
content_ai_response = get_response(thread)

for row in content_ai_response:
        if row.role == 'assistant':
            ai_response = row.content[0].text.value
    
print(ai_response)
