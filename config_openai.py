from dotenv import load_dotenv,dotenv_values


load_dotenv()
# values_env_openai = dotenv_values(".env")

# key = values_env_openai['searchkey']
# openai_api_key = values_env_openai['openai_api_key']
# openai_endpoint = values_env_openai['openai_endpoint']
# #location = values_env_openai['location']
# endpoint = values_env_openai['endpoint']
# index = values_env_openai['index']
# deployment_id_gpt4=values_env_openai['deployment_id_gpt4']

############## Without .Env file to execute on Azure Webapp
key = "BWsCKWR4hbERg9ErCTjTBEo932acdkdJArwfvhT47wAzSeDfEMYB"
openai_api_key = "4323387c308d4800ba0b46dad00cbf84"
openai_endpoint = "https://verofi-azure-openai.openai.azure.com"
#location = values_env_openai['location']
endpoint = "https://verofiazureaisearch.search.windows.net"
index = "veroindexall80p"
deployment_id_gpt4="vero-gpt-35-turbo"

