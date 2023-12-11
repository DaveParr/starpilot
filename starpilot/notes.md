## Wierd gotchas as I develop

### db -> as retiever -> get_documents is different api and behaviour to db -> similarity search

[db as retriever](https://python.langchain.com/docs/modules/data_connection/retrievers/vectorstore#specifying-top-k)
[db similarity search](https://api.python.langchain.com/en/latest/schema/langchain.schema.vectorstore.VectorStore.html?highlight=similarity_search#langchain.schema.vectorstore.VectorStore.similarity_search)

### When setting configuration through a dict, there is 0 response back if the arguments are implemented, acceptable, or entierly made up. 

This is correct
``` python
vectorstore_retrival = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=GPT4AllEmbeddings(disallowed_special=()),
    ).as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k, 
            "score_threshold": score_threshold,
            },
    )
```

This will execute with no indication of an issue
``` python
vectorstore_retrival = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=GPT4AllEmbeddings(disallowed_special=()),
    ).as_retriever(
        search_type="mmr",
        search_kwargs={
            "fetch_k": k, # made up key with sensible value
            "score_threshold": score_threshold,
            "fake_value": "fake" # made up key with made up value
            },
        },
    )
```

## Anti-pattern? - multiple document loaders for different document types

It's problematic to assume that because there are so many types of document loader, that the correct architecture is to upload each 'type' of document related to a single repo with a different model.

This is because:
* each call to create the document will be sequence 1 of 1
* it is harder to implement similar metadata needs without code repetition

Instead structure the response from the GitHub repo into a sensible set of json records that can be iterated over and uploaded to a single document loader and pass at the database.

## Comparators are note default across all vectorstores

Chroma only accepts a few comparators, and not all of the ones in the default prompt