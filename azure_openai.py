import openai
from config_openai import *
from openai import AzureOpenAI
from azure.cosmos import CosmosClient
import uuid
from datetime import datetime


# Initialize CosmosDB client
cosmos_client = CosmosClient(COSMOS_DB_ENDPOINT, credential=COSMOS_DB_KEY)
database = cosmos_client.get_database_client(DATABASE_NAME)
container = database.get_container_client(MULTI_CONV_CONTAINER_NAME)

now = datetime.now()
iso_string = now.isoformat()

# Initialize OpenAI client
client = AzureOpenAI(
  base_url=f"{openai_endpoint}/openai/deployments/{deployment_id_gpt4}/extensions", 
  api_key= openai_api_key,  
  api_version="2023-08-01-preview"
)

def store_chat_message(session_id, user_message, bot_response):
    """Stores chat history in CosmosDB."""
    chat_entry = {
        "id": str(uuid.uuid4()),  # Unique ID for each chat entry
        "sessionid": session_id,  # User session
        "timestamp": iso_string,
        "user_message": user_message,
        "bot_response": bot_response
    }
    container.create_item(body=chat_entry)

def fetch_chat_history(sessionid, limit=5):
    """Fetch last few messages from a session."""
    query = f"SELECT * FROM c WHERE c.sessionid='{sessionid}' ORDER BY c.timestamp DESC OFFSET 0 LIMIT {limit}"
    chat_history = list(container.query_items(query, enable_cross_partition_query=True))
    return chat_history[::-1]  # Return in chronological order

def create_prompt(context,query):
    header = "Type your vero.fi question here."
    return header + context + "\n\n" + query + "\n"


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
        temperature=0.0,
        top_p=0.1,
        #max_tokens=800,
        stop=None ,
        stream=False
    )
    return (response.choices[0].message.content).strip()
