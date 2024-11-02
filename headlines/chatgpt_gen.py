from openai import OpenAI
import tiktoken
import pandas as pd
from tqdm import tqdm
import json

client = OpenAI()

journalist_role = "You are a journalist working for a major US media outlet, where your role is to create compelling news stories while upholding journalistic honesty. Your task is to craft a catchy and engaging headline based on the results of a recent scientific experiment, designed to capture readers' attention and spark curiosity. Ensure the headline is concise and accessible to a broad audience.\nI want your response to be formatted as json like this:{'headline':'headline'}"

researcher_role = "You are a senior researcher who has conducted substantial research. You’ve been tasked with sharing your findings in a blog post for your university's website. This requires translating your technical work into language that is accessible to a general audience. Using the provided abstract of your publication, create a concise and engaging headline.\nI want your response to be formatted as json like this:{'headline':'headline'}"

user_content_journalist = "Given the following paragraph, generate a headline for the story." + "\n"
user_content_researcher = "Here is the abstract:"

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def get_response(system_content, user_content_query):
    completion = client.chat.completions.create(
        model = "gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content_query + "\nRespond in JSON format"}
        ]
    )
    return completion.to_dict()



def load_abstracts(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=0)
        abstracts = df['Abstract'].tolist()
        return abstracts
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return []

used_tokens = 0
abstracts = load_abstracts("dataset_headlines.xlsx")
gen_headlines = []
for abstract in tqdm(abstracts):
    completion = get_response(journalist_role, user_content_journalist + str(abstract))
    used_tokens += int(completion["usage"]["total_tokens"])
    output_info = json.loads(completion["choices"][0]["message"]["content"])
    print(output_info["headline"])
    gen_headlines.append(output_info["headline"])
print("Used tokens: ", used_tokens)

df = pd.DataFrame({"Titles": gen_headlines})
df.to_excel("journalist_chatgpt_headlines.xlsx", index=False)
