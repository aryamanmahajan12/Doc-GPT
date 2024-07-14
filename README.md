# Doc-GPT

Created a utility product to generate the 5 closest sentences to a certain query in a given document.

The closeness index is calculated for each query by computing the cosine similarity of the vector embedding of each query with the vector embeddings of individual chunks of the document.

The 5 closest sentences are converted into a prompt and fed to an LLM, such as ChatGPT. Based on retrieval augmented generation, the model outputs the answer to the query, given the pretext of the particular document.
