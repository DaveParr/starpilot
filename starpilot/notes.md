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