import openai
from config_openai import *
from openai import AzureOpenAI

# client = AzureOpenAI(
#   azure_endpoint = openai_endpoint, 
#   api_key= key,  
#   api_version="2023-09-01-preview"
# )
client = AzureOpenAI(
  base_url=f"{openai_endpoint}/openai/deployments/{deployment_id_gpt4}/extensions", 
  api_key= openai_api_key,  
  api_version="2023-08-01-preview"
)

def create_prompt(context,query):
    header = "Type your vero.fi question here."
    return header + context + "\n\n" + query + "\n"


# def generate_answer(conversation):
#     response = client.chat.completions.create(
#     model=deployment_id_gpt4,
#     messages=conversation,
#     temperature=0,
#     max_tokens=100,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0.8,
#     stream=False,
#     stop = None
#     )
#     print("----------------------------------------")
#     print(response)
#     print("----------------------------------------")
#     return (response.choices[0].message.content).strip()

def generate_answer(conversation):
    response = client.chat.completions.create(
        messages=conversation,
        model=deployment_id_gpt4,
        extra_body={
            "dataSources":[
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": endpoint,
                    "indexName": index,
                    "queryType": "simple",
                    "strictness": 3,
                    "key": key
                    }
                }
            ]},
        #enhancements=None,
        temperature=0,
        top_p=0.1,
        #max_tokens=800,
        stop=None ,
        stream=False
    )
    return (response.choices[0].message.content).strip()
