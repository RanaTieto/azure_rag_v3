
This repository contains the code for RAG process which developed using
Azure OpenAI
Azure CosmosDB
Azure Search Service
Azure Storage Account

This code were called using Azure App-Service and App Service plan.

UI was build on Azure App-Service.

Code description:
This code will accept the question and language, and then it will do the semantic search on Azure Search Service, and it will send semantic search result to Azure OpenAI to generate response using that data-set,
and this response will be sent back to calling API.
It will receive the feedback also for each question and answer, and these question, answer and feedback will be stored in Cosmos DB.


