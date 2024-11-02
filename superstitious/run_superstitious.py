from openai import OpenAI
import tiktoken
import pandas as pd
import json
import google.generativeai as genai
import os
import anthropic
from scipy import stats

# ChatGPT
client = OpenAI()
# Gemini
genai.configure(api_key=os.environ["API_KEY"])
# Claude
client_claude = anthropic.Anthropic()

system_content = ""
user_content = "\nI want your response to be formatted as json like this:{'response':'number'}"

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

def claude_get_response(system_content, user_content_query):
    message = client_claude.messages.create(
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

def gemini_get_response(system_content, user_content_query):
  """
  Sends a request to the Gemini API and returns the generated headline.
  """
  try:
    model=genai.GenerativeModel(
    model_name="gemini-1.5-pro")

    response = model.generate_content(user_content_query)
    r = response.text.replace("```json\n","").replace("```","")
    return r
  except Exception as e:
     return str(e)

def chatgpt_get_response(system_content, user_content_query):
    completion = client.chat.completions.create(
        model = "gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content_query}
        ]
    )
    return completion.to_dict()

superstitious_dataset = pd.read_excel('results.xlsx', sheet_name=0)

def query_chatgpt(superstitious_dataset):
    used_tokens = 0
    scores = []
    for index, row in superstitious_dataset.iterrows():
            completion = chatgpt_get_response("", row['Prompt'] + user_content)
            output_info = json.loads(completion["choices"][0]["message"]["content"])
            print(output_info["response"])
            scores.append(output_info["response"])
    print("Used tokens: ", used_tokens)
    output = pd.DataFrame({'responses': scores})
    output.to_excel('chatgpt_output.xlsx', index=False)

def query_gemini(superstitious_dataset):
    scores = []
    for index, row in superstitious_dataset.iterrows():
        completion = gemini_get_response("", row['Prompt'] + user_content)
        print(completion)
        scores.append(completion)
    output = pd.DataFrame({'responses': scores})
    output.to_excel('gemini_output.xlsx', index=False)

def query_claude(superstitious_dataset):
   scores = []
   for index, row in superstitious_dataset.iterrows():
        completion = claude_get_response("", row['Prompt'] + user_content)
        print(completion)
        scores.append(completion)
   output = pd.DataFrame({'responses': scores})
   output.to_excel('claude_output.xlsx', index=False)

def compute_statistical_sign(superstitious_dataset):
    # Prueba t entre pares de columnas
    comparisons = [
        ('ChatGPT', 'Claude'),
        ('ChatGPT', 'Gemini'),
        ('Claude', 'Gemini')
    ]

    for col1, col2 in comparisons:
        t_stat, p_value = stats.ttest_ind(superstitious_dataset[col1], superstitious_dataset[col2])
        if p_value < 0.05:
            print(f"{col1} vs {col2}: significancia estadística, p-value = {p_value:.4f} ({p_value})")

#query_gemini(superstitious_dataset)
compute_statistical_sign(superstitious_dataset)
