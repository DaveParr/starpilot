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

## Comparators are not default across all vectorstores

Chroma only accepts a few comparators, and not all of the ones in the default prompt

## Converting from REST to GraphQL

By using the graphql endpoint all the information for up 100 repos can be retrieved in a single call, therefore this call can be iterated over a number of times = number of repos / 100. For 500 repos thats 5 calls.

Previously 1 call was needed to gather all the git hub starred repos, then for each repo 9 calls were needed to get the relevant information. For 500 repos this is therefore 500 * 9 = 4500 calls.

The overhead required to set up and run the calls, then process and append each piece of information meant for 500 repos the user time was around 20 minutes to gather all the information from github. 

Ignoring the time benefit of the graphql endpoint, there is no straightforward way to push a filter on teh results up to github. You just ask for the first 100 repos, ordered by the date starred, then the next 100, and so on. However, the graphql endpoint also handles 'missing fields' by returning null instead of throwing an error. This means the missing data can be handled with normal python logic, instead of having to write a try except block for each piece of data. 

The graphql query is more prone to timeout though, and the timeout is not handled well by the python library. Interestingly the timeout is triggered by the data points _requested_, not those that are present. 

e.g. asking for a repos topics first=100 will timeout, but a repos topics first=10 will not.

## Typing in Langsmith is frequently incorrect

Because LangChain is a fast developing project, and most of the functions and methods can be stuffed with extra arguments which get passed on to different functions, the typing is frequently incorrect. This is made worse when the docs [actively suggest code](https://python.langchain.com/docs/modules/data_connection/retrievers/self_query#constructing-from-scratch-with-lcel:~:text=The%20next%20key,Integrations%20section.) like this:

``` python
from langchain.retrievers.self_query.chroma import ChromaTranslator

retriever = SelfQueryRetriever(
    query_constructor=query_constructor,
    vectorstore=vectorstore,
    structured_query_translator=ChromaTranslator(),
)
```

which is reported to pylance as:

``` json
[{
	"resource": "/home/dave/Development/starpilot/starpilot/main.py",
	"owner": "_generated_diagnostic_collection_name_#4",
	"code": {
		"value": "reportCallIssue",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportCallIssue"
		}
	},
	"severity": 8,
	"message": "Argument missing for parameter \"llm_chain\"",
	"source": "Pylance",
	"startLineNumber": 252,
	"startColumn": 17,
	"endLineNumber": 257,
	"endColumn": 6
},
{
	"resource": "/home/dave/Development/starpilot/starpilot/main.py",
	"owner": "_generated_diagnostic_collection_name_#4",
	"code": {
		"value": "reportCallIssue",
		"target": {
			"$mid": 1,
			"path": "/microsoft/pyright/blob/main/docs/configuration.md",
			"scheme": "https",
			"authority": "github.com",
			"fragment": "reportCallIssue"
		}
	},
	"severity": 8,
	"message": "No parameter named \"query_constructor\"",
	"source": "Pylance",
	"startLineNumber": 253,
	"startColumn": 9,
	"endLineNumber": 253,
	"endColumn": 26
}]
```

but actually is runnable and correct?


## Langchain has bad local logging becuase it wants you to use langsmith

Langchain the company seemed like they just weren't interested in local logging. `verbose=true` seems to not actually do anything in many cases, and grabbing information out of chains during runtime either gives lots of pointless model card information which is not useful, or forces a process of function wrapping or avoiding LCEL. 

Instead they've been developing an extremely complex cloud observability tool called Langsmith. It is defintely useful, and easy to set up and currently has a generous free personal tier. However it does seem a little disingeous to not have a local logging solution, even if the 'new paradigm' of LLM/AI does pose some challenges to traditional logging.

These challenges seem to be:

logging run detail and then aggregating across a number of runs and parameters is more valuable than logging the detail of a single run
langchain is effectively a data orchestration tool, so the path of a run can vary significantly even with no code changes
llm/ai is inherently non-deterministic, so the same code can produce different results