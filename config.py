from dotenv import load_dotenv
from dotenv import dotenv_values


load_dotenv()
# values_env = dotenv_values(".env")

# #Azure Search Service
# searchservice = values_env['searchservice']
# index = values_env['index']
# searchkey = values_env['searchkey']
# category=values_env['category']

# #AZURE STORAGE CONFIGURATION
# storageaccount  = values_env['storageaccount']
# container=values_env['container']
# storagekey=values_env['storagekey']

# localpdfparser=values_env['localpdfparser']
# verbose=values_env['verbose']

# FILE_PATH = values_env['FILE_PATH']

# formrecognizerservice=values_env['formrecognizerservice']


############## Without .Env file to execute on Azure Webapp
searchservice = "verofiazureaisearch"
index = "veroindexall80p" #"veroindexcar"
searchkey = "BWsCKWR4hbERg9ErCTjTBEo932acdkdJArwfvhT47wAzSeDfEMYB"
category="SEARCH"
#AZURE STORAGE CONFIGURATION
storageaccount  = "verofitest"
container="raw"
storagekey="ue6AkGVkrscy4ffi8fEukAxGjJ31nMc9rpgbT6tDBZMIL7SwYYC4EIfOGRkviLMIVYyaiohEO417+AStbWHEQw=="
localpdfparser=True
verbose=True
FILE_PATH = "C:\\Users\\kumasran\\OneDrive - Tietoevry\\Desktop\\own\\Jai_Sri_Ram\\Whitepaper\\AI_RAG\\verofidata" #"C:\Users\kumasran\OneDrive - Tietoevry\Desktop\own\Jai_Sri_Ram\Whitepaper\AI_RAG\verofidata"
formrecognizerservice=""
