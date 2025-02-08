import os
import argparse
import glob
import html
import io
import re
import time
from pypdf import PdfReader, PdfWriter
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure_openai import *
from config import *
from deep_translator import GoogleTranslator




#user_input = 'When car tax was updated?'
#user_input = "Milloin autovero on päivitetty?"
user_input = "kun autovero päivitettiin"
#user_input = 'Who is the president of america? Dont get data from training data'
#user_input = 'Who is the president of america?'
#user_input = 'is there discount on car if it is registered after 1 July 2023'

service_name = searchservice
key = searchkey

endpoint = "https://{}.search.windows.net/".format(searchservice)
index_name = index

azure_credential =  AzureKeyCredential(key)

search_client = SearchClient(endpoint=endpoint,
                                    index_name=index_name,
                                    credential=azure_credential)


KB_FIELDS_CONTENT = os.environ.get("KB_FIELDS_CONTENT") or "content"
KB_FIELDS_CATEGORY = os.environ.get("KB_FIELDS_CATEGORY") or category
KB_FIELDS_SOURCEPAGE = os.environ.get("KB_FIELDS_SOURCEPAGE") or "sourcepage"

exclude_category = None

print("Searching:", user_input)
user_input = GoogleTranslator(source='auto', target='en').translate(user_input)

print("Searching in English:", user_input)
print("-------------------")
filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None
r = search_client.search(user_input, 
                        filter=filter,
                        query_type=QueryType.SEMANTIC, 
                        query_language= "en-us",
                        query_speller="lexicon", 
                        semantic_configuration_name="default", 
                        top=3)
#print("rrrrrr=",r)
results = [doc[KB_FIELDS_SOURCEPAGE] + ": " + doc[KB_FIELDS_CONTENT].replace("\n", "").replace("\r", "") for doc in r]
content = "\n".join(results)
#print("content=",content)

references =[]
for result in results:
    references.append(result.split(":")[0])
#print("references=",references)

conversation=[{"role": "system", "content": "Dont response from model training data."}]
conversation.append({"role": "assistant", "content": "use content data only."})
prompt = create_prompt(content,user_input)            
conversation.append({"role": "assistant", "content": prompt})
conversation.append({"role": "user", "content": user_input})
#print("conversation===",conversation)
reply = generate_answer(conversation)
reply = GoogleTranslator(source='auto', target='fi').translate(reply)
print(reply)