import os
import re
from pypdf import PdfReader, PdfWriter
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure_openai import store_chat_message, fetch_chat_history
from config_openai import *
from openai import AzureOpenAI
import numpy as np
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
    session_id: str = None

class rag_feedback(BaseModel):
    feedback: int
    response: str

@app.get("/")
def read_root():
    return {"Welcome": "Vero.fi Q&A."}


@app.post("/question")
async def read_root(rag_question: rag_question):
    #return {"Hello": f" Vero.fi Q&A in {rag_question.language} for {rag_question.question}"}
    return rag_qanda(rag_question.question, rag_question.language,rag_question.session_id)

@app.post("/feedback")
async def post(rag_feedback: rag_feedback):
    #return {"Message:": f"{rag_feedback.response} in Post {rag_feedback.feedback}"}
    return rag_feedback_response(rag_feedback.feedback,rag_feedback.response)

def rewrite_followup_query(user_query, chat_history):
    """
    If the user query contains vague references like 'that' or 'it',
    rewrite it using the previous message.
    """
    if len(chat_history) > 0:
        last_question = chat_history[-1]["user_message"]
        # Replacing vague references
        if re.search(r"\b(it|that|this)\b", user_query, re.IGNORECASE):
            return f"Regarding '{last_question}', {user_query}"
    return user_query

## Implementing Hallucination Detection Using Similarity Check
# Function to generate embeddings using OpenAI or Azure OpenAI
def get_embedding(text):
    client = AzureOpenAI(
        api_key=openai_api_key,
        api_version="2023-05-15",
        azure_endpoint=f"https://verofi-azure-openai.openai.azure.com"
    )
#     client = AzureOpenAI(
#   base_url=f"{openai_endpoint}/openai/deployments/{deployment_id_gpt4}/extensions", 
#   api_key= openai_api_key,  
#   api_version="2023-08-01-preview"
# )
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return np.array(response.data[0].embedding)  # Convert to NumPy array for comparison

# Function to calculate cosine similarity
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def rag_qanda(question, lang_choise, session_id=None):
    if lang_choise.lower() == "english":
        tgt_lang = 'en'
    elif lang_choise.lower() == "finnish":
        tgt_lang = 'fi'
    elif lang_choise.lower() == 'swedish':
        tgt_lang = 'sv'
    else:
        tgt_lang = 'en'
    
    # Gen(erate session ID if not provided
    print("session_id=====",session_id)
    if not session_id:
        print("No Session Id Passed.")
        import uuid
        session_id = str(uuid.uuid4())
    
    # Fetch chat history (last 5 messages)
    chat_history = fetch_chat_history(session_id, limit=5)
    print("chat_history=====",chat_history)
    # conversation_context = "\n".join(
    #     [f"User: {chat['user_message']}\nBot: {chat['bot_response']}" for chat in chat_history]
    # )
    # Format chat history correctly
    conversation_context = ""
    for chat in chat_history:
        conversation_context += f"User: {chat['user_message']}\nBot: {chat['bot_response']}\n"

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
    user_input = rewrite_followup_query(user_input, chat_history)
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

    # Create conversation-aware prompt
    # Create conversation-aware prompt
    prompt = f"""
    You are an AI assistant helping users by maintaining conversation context. Answer questions based on prior interactions. If the user's new question references something from past messages (like 'it' or 'this'), refer to the last relevant topic.

    Past conversation:
    {conversation_context}

    Context from retrieved documents:
    {content}

    New User Question: {user_input}

    Rephrase the user's latest question to make it self-contained before answering. If needed, infer missing details from the past conversation.
    ### Follow this step-by-step approach before answering ###
    1. **Break down the question logically** into smaller steps.
    2. **Retrieve relevant information** from the conversation history and the retrieved documents.
    3. **Explain each step clearly**, ensuring logical flow.
    4. **Provide the final answer in a structured format**.

    **Now generate a well-structured response using this approach.**
    """

    references =[]
    for result in results:
        references.append(result.split(":")[0])
    #st.markdown("### References:")
    #st.write(" , ".join(set(references)))
    print("reference=====",references)
    print("prompt=====",prompt)

    conversation=[{"role": "system", "content": "Assistant is a great language model formed by OpenAI."}]
    # Generate answer from OpenAI
    conversation = [{"role": "system", "content": "You are a knowledgeable tax assistant who follows step-by-step reasoning before answering."},
                    {"role": "assistant", "content": prompt},
                    {"role": "user", "content": user_input}]
    reply = generate_answer(conversation)

    ## Hallucination Detection based onn similarity check
    if HALLUCINATION_SIMILAR_BASED:
        retrieved_embedding = get_embedding(content)
        response_embedding = get_embedding(reply)
        similarity_score = cosine_similarity(response_embedding, retrieved_embedding)
        if similarity_score < HALLUCINATION_SIMILAR_THRESHOLD:
            reply = "\n\n⚠️ Warning: This answer may not be fully supported by retrieved documents."
    ## End of Hallucination Detection, Comment out if not needed
    ## Hallucination Detection using LLM-Based Revalidation
    if HALLUCINATION_LLM_BASED:
        validation_prompt = f"""
        You are an AI tasked with validating answers against provided documents:
        
        ### Retrieved Documents ###
        {content}

        ### Given Answer ###
        {reply}

        ### Strict Verification Rules ###
        1️⃣ **Check if the answer is supported by the retrieved documents, even if it is paraphrased.**  
        2️⃣ **If the answer is correct but worded differently, mark it as verified.**  
        3️⃣ **If the answer contains unsupported details, remove them but keep the correct parts.**  
        4️⃣ **If no relevant information exists at all, return: "No relevant document found."*

        ### Strictly Verified Answer (DO NOT DEVIATE FROM THESE RULES) ###
        """
        validate_answer = [{"role": "user", "content": validation_prompt}]
        validated_answer = generate_answer(validate_answer)
        if "I don't know" in validated_answer or "not supported" in validated_answer.lower() or "not contain any information" in validated_answer.lower() or "no verified information" in validated_answer.lower() or validated_answer.strip() == "":
            reply = "⚠️ Warning: The answer could not be fully verified. Please consult official tax sources."
    ## End of Hallucination Detection, Comment out if not needed

    if lang_choise.lower() != "english":
        reply = GoogleTranslator(source='en', target=tgt_lang).translate(reply) #source could be auto also
    feedback = uniq_number()
    answer = re.sub(r'\[doc\d+]', '',reply)
    store_chat_message(session_id, actual_user_input, answer)
    cosmosdb_insert_data(feedback,actual_user_input,answer,"",lang_choise.lower())
    return {"answer": answer, "feedback": feedback, "session_id": session_id}

def uniq_number():
    from datetime import datetime
    return int(datetime.now().strftime('%m%d%H%M%S'))

def rag_feedback_response(feedback,response):
    try:
        cosmosdb_update_response(feedback,response)
        return {"Message:": "Ok", "Status:": 200}
    except Exception as e:
        raise Exception("Failed to update Response.",e)
