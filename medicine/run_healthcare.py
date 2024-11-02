from openai import OpenAI
import tiktoken
import pandas as pd
from tqdm import tqdm
import json
import google.generativeai as genai
import os
import anthropic
import ast

# ChatGPT
client = OpenAI()
# Gemini
genai.configure(api_key=os.environ["API_KEY"])
# Claude
client_claude = anthropic.Anthropic()

system_content = ""
user_content = """\nI want your response to be formatted as json like this:{"effectiveness":"scale"}"""

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
    model_name="gemini-1.5-pro",
    system_instruction=system_content)

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

medical_records = pd.read_excel('gen_medical_records.xlsx', sheet_name=0)
medical_records = medical_records[40:]

output = pd.DataFrame({'results':[]})
output.to_excel('claude_output.xlsx', index=False)
# 100 listas de 10 scores cada una
scores = []
for index, row in medical_records.iterrows():
    # par de variables
    cause = row['Cause']
    effect = row['Effect']
    # Combinaciones
    local_list = ast.literal_eval(row['gen_medical_records'])
    # lista con 10 scores, un score por cada lista de [20-100] pacientes
    local_scores = []
    for k, v in local_list.items():
        comb_lista = []
        for lista in v:
            lista = ast.literal_eval(lista)
            comb = f'{cause}:{lista[0]}, {effect}:{lista[1]}'
            comb_lista.append(comb)
        # Consultar al modelo por un score enviando comb_lista
        #completion = chatgpt_get_response(row['Prompt'], " .These are the medical records:" + str(comb_lista) + user_content)
        #completion = gemini_get_response(row['Prompt'], " .These are the medical records:" + str(comb_lista) + user_content)
        completion = claude_get_response(row['Prompt'], " .These are the medical records:" + str(comb_lista) + user_content)
        #output_info = json.loads(completion["choices"][0]["message"]["content"])
        #print(output_info["effectiveness"])
        #print(completion)
        local_scores.append(completion)
        #local_scores.append(int(output_info["effectiveness"]))
    # Guarda el resultado parcial en el archivo Excel
    output = pd.DataFrame({'results': [local_scores]})
    with pd.ExcelWriter('claude_output.xlsx', engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        output.to_excel(writer, index=False, header=False, startrow=index + 1)  # Escribe en la siguiente fila
    scores.append(local_scores)
