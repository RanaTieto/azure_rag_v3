
import os
#from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.cosmos import CosmosClient,PartitionKey # import CosmosClient 
import json
import asyncio

# Cosmos-DB configuration
URL = "https://db-vero-fi-data.documents.azure.com:443/"
KEY = "XmHjs8RqqXWVIBwiWMQK6JXSYJwgPkMByM3FV9mOEG5ICq2s9mvLgcPHqD9DoZXlwJ179m08xeqQACDbcnlKOw=="
DATABASE_NAME = 'db_conversation_history'
CONTAINER_NAME = 'verofi_conversations'
COLUMN_NAME='/feedback'
create_db_if_not_exist = False
create_container_if_not_exist = True


client = CosmosClient(URL, credential=KEY)



def cosmosdb_database_check(DATABASE_NAME):
    try:
        database = client.get_database_client(DATABASE_NAME)
        dbid = database.read()
        return database
    except Exception as e:
        raise Exception("Failed to load CosmosDB database.")

def cosmosdb_container_check(database, CONTAINER_NAME):
    try:
        container = database.get_container_client(CONTAINER_NAME)
        conid = container.read()
        return container
    except Exception as e:
        raise Exception("Failed to load CosmosDB Container.")

def cosmosdb_create_database(DATABASE_NAME):
    try:
        database = client.create_database(DATABASE_NAME)
        client.get_database_client(database)
        return cosmosdb_database_check(DATABASE_NAME)
    except Exception as e:
        raise Exception ("Failed to create CosmosDB Database.",e)

def cosmosdb_create_dbcontainer(database, CONTAINER_NAME, COLUMN_NAME):
    try:
        container = database.create_container(id=CONTAINER_NAME, partition_key=PartitionKey(path=COLUMN_NAME, kind='Hash'))
        return cosmosdb_container_check(database, CONTAINER_NAME)
    except Exception as e:
        raise Exception ("Failed to create CosmosDB Database Container.",e)

try:
    database = cosmosdb_database_check(DATABASE_NAME)
except Exception as e:
    if create_db_if_not_exist:
        try:
            database = cosmosdb_create_database(DATABASE_NAME)
        except Exception as e:
            raise Exception ("Failed to Setup CosmosDB Database.")
    else:
        raise Exception ("CosmosDB database is missing.")


try:
    container = cosmosdb_container_check(database, CONTAINER_NAME)
except Exception as e:
    if create_container_if_not_exist:
        try:
            container = cosmosdb_create_dbcontainer(database, CONTAINER_NAME, COLUMN_NAME)
        except Exception as e:
            raise Exception ("Failed to Setup CosmosDB Database Container.")
    else:
        raise Exception ("CosmosDB Contianer is missing.")

def cosmosdb_insert_data(feedback, question, answer, response, language):
    try:
        container.upsert_item({
            'id': '{}'.format(feedback),
            'feedback': feedback,
            'question': question,
            'answer': answer,
            'response': response,
            'language': language
        })
        return True
    except Exception as e:
        raise Exception ("Failed to insert data in container.",e)

def cosmosdb_update_response(feedback, response):
    try:
        for item in container.query_items(query=f"select ver.id,ver.feedback,ver.question,ver.answer,ver.response,ver.language from {CONTAINER_NAME} ver where ver.feedback={feedback}",enable_cross_partition_query=True):
            item['response'] = response
            print(json.dumps(item, indent=False))
            container.upsert_item({
            'id': item['id'],
            'feedback': item['feedback'],
            'question': item['question'],
            'answer': item['answer'],
            'response': item['response'],
            'language': item['language']
        })
        return True
    except Exception as e:
        raise Exception ("Failed to update data in container.",e)

#cosmosdb_insert_data(4125782544,"When car tax was updated","That stulasd sdfas df asd fa","")
#cosmosdb_update_response(4125782544,"Very Happy")
