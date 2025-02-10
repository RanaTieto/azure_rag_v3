from dotenv import load_dotenv,dotenv_values

load_dotenv()

############## Without .Env file to execute on Azure Webapp
key = "BWsCKWR4hbERg9ErCTjTBEo932acdkdJArwfvhT47wAzSeDfEMYB"
openai_api_key = "4323387c308d4800ba0b46dad00cbf84"
openai_endpoint = "https://verofi-azure-openai.openai.azure.com"
#location = values_env_openai['location']
endpoint = "https://verofiazureaisearch.search.windows.net"
index = "veroindexall80p"
deployment_id_gpt4="vero-gpt-35-turbo"

############## CosmosDB Configuration
COSMOS_DB_ENDPOINT = "https://db-vero-fi-data.documents.azure.com:443/"
COSMOS_DB_KEY = "XmHjs8RqqXWVIBwiWMQK6JXSYJwgPkMByM3FV9mOEG5ICq2s9mvLgcPHqD9DoZXlwJ179m08xeqQACDbcnlKOw=="
DATABASE_NAME = 'db_conversation_history'
MULTI_CONV_CONTAINER_NAME = 'VeroMultiTurnConv'
MULTI_CONV_PARTION_COLUMN='/sessionid'

HALLUCINATION_LLM_BASED = True
HALLUCINATION_SIMILAR_BASED = True
HALLUCINATION_SIMILAR_THRESHOLD = 0.6
