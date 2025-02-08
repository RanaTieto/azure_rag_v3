import os
import re
from pypdf import PdfReader, PdfWriter
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure_openai import *
from config import *
from feedback import *
from fastapi import FastAPI
from pydantic import BaseModel
import re
from deep_translator import GoogleTranslator

app = FastAPI()

class rag_question(BaseModel):
    question: str
    language: str = ["English", "Finnish", "Swedish"]

class rag_feedback(BaseModel):
    feedback: int
    response: str

@app.get("/")
def read_root():
    return {"Welcome": "Vero.fi Q&A."}


@app.post("/question")
async def read_root(rag_question: rag_question):
    #return {"Hello": f" Vero.fi Q&A in {rag_question.language} for {rag_question.question}"}
    return rag_qanda(rag_question.question, rag_question.language)

@app.post("/feedback")
async def post(rag_feedback: rag_feedback):
    #return {"Message:": f"{rag_feedback.response} in Post {rag_feedback.feedback}"}
    return rag_feedback_response(rag_feedback.feedback,rag_feedback.response)


def rag_qanda(question, lang_choise):
    if lang_choise.lower() == "english":
        tgt_lang = 'en'
    elif lang_choise.lower() == "finnish":
        tgt_lang = 'fi'
    elif lang_choise.lower() == 'swedish':
        tgt_lang = 'sv'
    else:
        tgt_lang = 'en'

    user_input = question
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
    actual_user_input = user_input
    if lang_choise != "English":
        user_input = GoogleTranslator(source='auto', target='en').translate(user_input)
    print("-------------------")
    filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None
    r = search_client.search(user_input, 
                            filter=filter,
                            query_type=QueryType.SEMANTIC, 
                            query_language="en-US", 
                            query_speller="lexicon", 
                            semantic_configuration_name="default", 
                            top=3)
    results = [doc[KB_FIELDS_SOURCEPAGE] + ": " + doc[KB_FIELDS_CONTENT].replace("\n", "").replace("\r", "") for doc in r]
    content = "\n".join(results)

    references =[]
    for result in results:
        references.append(result.split(":")[0])
    #st.markdown("### References:")
    #st.write(" , ".join(set(references)))
    print("reference=====",references)

    conversation=[{"role": "system", "content": "Assistant is a great language model formed by OpenAI."}]
    prompt = create_prompt(content,user_input)            
    conversation.append({"role": "assistant", "content": prompt})
    conversation.append({"role": "user", "content": user_input})
    reply = generate_answer(conversation)

    if lang_choise.lower() != "english":
        reply = GoogleTranslator(source='en', target=tgt_lang).translate(reply) #source could be auto also
    feedback = uniq_number()
    answer = re.sub(r'\[doc\d+]', '',reply)
    cosmosdb_insert_data(feedback,actual_user_input,answer,"",lang_choise.lower())
    return {"answer": answer, "feedback": feedback}

def uniq_number():
    from datetime import datetime
    return int(datetime.now().strftime('%m%d%H%M%S'))

def rag_feedback_response(feedback,response):
    try:
        cosmosdb_update_response(feedback,response)
        return {"Message:": "Ok", "Status:": 200}
    except Exception as e:
        raise Exception("Failed to update Response.",e)
