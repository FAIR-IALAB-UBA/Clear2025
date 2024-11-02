import anthropic
import pandas as pd
from tqdm import tqdm
import time

journalist_role = """You are a journalist working for a major US media outlet, where your role is to create compelling news stories while upholding journalistic honesty. Your task is to craft a catchy and engaging headline based on the results of a recent scientific experiment, designed to capture reader's attention and spark curiosity. Ensure the headline is concise and accessible to a broad audience.\nI want your response to be formatted as json. Use this JSON schema:{"headline":str}"""

researcher_role = """You are a senior researcher who has conducted substantial research. You’ve been tasked with sharing your findings in a blog post for your university's website. This requires translating your technical work into language that is accessible to a general audience. Using the provided abstract of your publication, create a concise and engaging headline.\nI want your response to be formatted as json. Use this JSON schema:{"headline":str}"""

user_content_journalist = "Given the following paragraph, generate a headline for the story." + "\n"
user_content_researcher = "Here is the abstract:"


client = anthropic.Anthropic()

def get_response_claude(system_content, user_content_query):
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system=system_content,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_content_query,
                    }
                ]
            }
        ]
    )
    return message.content[0].text


def load_transcriptions(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        transcriptions = df['Abstract'].tolist()
        return transcriptions
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return []

used_tokens = 0
abstracts = load_transcriptions("dataset_headlines.xlsx")
gen_titles = []
for abstract in tqdm(abstracts):
  response = get_response_claude(journalist_role, user_content_journalist + str(abstract))
  gen_titles.append(response)
print("Headlines generated!")

df = pd.DataFrame({"Titles": gen_titles})
df.to_excel("journalist_claude_headlines.xlsx", index=False)
