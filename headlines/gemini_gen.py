import requests
import json
import pandas as pd
import time
from tqdm import tqdm

import google.generativeai as genai
import os

genai.configure(api_key=os.environ["API_KEY"])

journalist_role = """You are a journalist working for a major US media outlet, where your role is to create compelling news stories while upholding journalistic honesty. Your task is to craft a catchy and engaging headline based on the results of a recent scientific experiment, designed to capture reader's attention and spark curiosity. Ensure the headline is concise and accessible to a broad audience.\nI want your response to be formatted as json. Use this JSON schema:{"headline":str}"""

researcher_role = """You are a senior researcher who has conducted substantial research. You’ve been tasked with sharing your findings in a blog post for your university's website. This requires translating your technical work into language that is accessible to a general audience. Using the provided abstract of your publication, create a concise and engaging headline.\nI want your response to be formatted as json. Use this JSON schema:{"headline":str}"""

user_content_journalist = "Given the following paragraph, generate a headline for the story." + "\n"
user_content_researcher = "Here is the abstract:"

def get_response(system_content, user_content_query):
  """
  Sends a request to the Gemini API and returns the generated headline.
  """
  try:
    model=genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=system_content)

    response = model.generate_content(user_content_query)
    r = response.text.replace("```json\n","").replace("```","")
    return r
  except Exception as e:
     return str(e)

def load_transcriptions(file_path):
    try:
        # Lee el archivo Excel
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
  response = get_response(journalist_role, user_content_journalist + str(abstract))
  gen_titles.append(response)
print("Headlines generated!")

df = pd.DataFrame({"Titles": gen_titles})
df.to_excel("journalist_gemini_headlines.xlsx", index=False)