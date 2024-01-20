import os
import faiss
import time
import pickle
import numpy as np
from dotenv import load_dotenv
from typing import List

from bot.database import connect_to_postgres, retrieve_first_n_rows, retrieve_all_rows
from bot.openai import convert_text_to_embedding

load_dotenv()

class FaissDatabase:
    """ A database class for storing and searching embeddings using Faiss. """
    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.ids = []
        self.titles = []
        self.texts = []
        self.embeddings = []
        self.existing_ids = set()

    def insert_data(self, data: tuple) -> None:
        """ Insert data into the database.
        Args:
            ids (list): List of IDs.
            embeddings (list): List of embeddings.
            texts (list): List of texts.
        """
        ids = [item[0] for item in data]
        titles = [item[1] for item in data]
        texts = [item[2] for item in data]
        embeddings = [item[3] for item in data]

        if len(ids) == 0 or len(embeddings) == 0 or len(texts) == 0:
            raise ValueError("IDs, embeddings, and texts must not be empty.")

        if not (len(ids) == len(embeddings) == len(texts)):
            raise ValueError("IDs, embeddings, and texts must be of the same length.")

        # filter out records that already exist
        new_data = [(id, title, text, embedding) for id, title, text, embedding in zip(ids, titles, texts, embeddings) if id not in self.existing_ids]
        if not new_data:
            return
        
        new_ids, new_titles, new_texts, new_embeddings = zip(*new_data)
        self.existing_ids.update(new_ids)

        np_embeddings = np.array(new_embeddings).astype('float32')
        np_embeddings = self.normalize_embeddings(np_embeddings)

        self.index.add(np_embeddings)

        self.ids.extend(new_ids)
        self.titles.extend(new_titles)
        self.texts.extend(new_texts)
        self.embeddings.extend(new_embeddings)

    def normalize_embeddings(self, embeddings):
        """ Normalize the embeddings.
        Args:
            embeddings (list): List of embeddings.
        Returns:
            list: List of normalized embeddings.
        Example:
            >>> embeddings_norm = db.normalize_embeddings(embeddings)
        """
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        return embeddings / norms

    def search(self, query_embedding, k):
        query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)
        query_embedding = self.normalize_embeddings(query_embedding)  # Normalize query embedding
        distances, indices = self.index.search(query_embedding, k)
        return [(self.ids[idx], self.texts[idx], distances[0][i]) for i, idx in enumerate(indices[0])]

    def search_cosine_knn(self, query_embedding, k):
        """ Search cosine for the k nearest neighbors of the query embedding.
        To use cosine similarity in Faiss, normalize the vectors and use an L2 distance index, as cosine similarity is equivalent
        to L2 distance after normalization.
        Args:
            query_embedding (list): The query embedding.
            k (int): The number of nearest neighbors to retrieve.
        Returns:
            list: A list of tuples containing the IDs, texts, and distances of the k nearest neighbors.
        Example:
            >>> results = db.search_cosine_knn(query_embedding, k=5)
        """
        query_embedding = np.array(query_embedding).astype('float32').reshape(1, -1)
        query_embedding = self.normalize_embeddings(query_embedding)
        distances, indices = self.index.search(query_embedding, k)
        return [(self.ids[idx], self.titles[idx], self.texts[idx], distances[0][i]) for i, idx in enumerate(indices[0])]

    def find_index_by_id(self, target_id):
        """ Find the index of a target ID in a list of IDs.

        Args:
            target_id: The ID to search for.

        Returns:
            int: The index of the target ID in the list, or -1 if not found.
        """
        try:
            index = self.ids.index(target_id)
            return index
        except ValueError:
            return -1

    def save_index(self, file_path: str):
        """ Save the Faiss index into a file.
        Args:
            file_path (str): The path to the file to save the index to.
        Example:
            >>> db.save_index('index.faiss')
        """
        faiss.write_index(self.index, file_path)

    def load_index(self, file_path: str):
        """ Load the Faiss index from a file.
        Args:
            file_path (str): The path to the file to load the index from.
        Example:
            >>> db.load_index('index.faiss')
        """
        self.index = faiss.read_index(file_path)

    def save_metadata(self, file_path: str):
        """ Save additional data (ids and texts)
        Args:
            file_path (str): The path to the file to save the metadata to.
        Example:
            >>> db.save_metadata('metadata.pkl')
        """
        with open(file_path, 'wb') as f:
            pickle.dump({'ids': self.ids, 
                         'titles': self.titles,
                         'texts': self.texts,
                         'embeddings': self.embeddings}, f)

    def load_metadata(self, file_path: str):
        """ Load additional data (ids and texts)
        Args:
            file_path (str): The path to the file to load the metadata from.
        Example:
            >>> db.load_metadata('metadata.pkl')
        """
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
            self.ids = data['ids']
            self.titles = data['titles']
            self.texts = data['texts']
            self.embeddings = data['embeddings']


api_key = os.getenv('OPENAI_TOKEN')
db_password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('POSTGRES_DB')
db_table = os.getenv('POSTGRES_TABLE')
db_port = os.getenv('POSTGRES_PORT')

conn, cursor = connect_to_postgres(password=db_password, database=db_name, port=db_port)
#data = retrieve_first_n_rows(n=20, cursor=cursor, table_name=db_table)
data = retrieve_all_rows(cursor=cursor, table_name=db_table)

embedding_dim = 1536
db = FaissDatabase(embedding_dim)

# # === insert embeddings into vector index === #
# for i, item in enumerate(data):
#     print(f"Processing item {i} of {len(data)} ...")
#     embedding = convert_text_to_embedding(item[2].replace("\n", " "), api_key)
#     data[i] = (*item, embedding)
#     if i % 10 == 0:
#         time.sleep(1)

# print("Inserting data into vector index ...")
# db.insert_data(data)
# # === end of inserting embeddings into vector index === #
#
# # === save index and metadata === #
# print("Saving index and metadata ...")
# db.save_index('faiss_db/index.faiss')
# db.save_metadata('faiss_db/metadata.pkl')
# print("Finished saving index and metadata.")
# # === end of saving index and metadata === #

# === load index and metadata === #
print("Loading index and metadata ...")
db.load_index('faiss_db/index.faiss')
db.load_metadata('faiss_db/metadata.pkl')
print("Finished loading index and metadata.")

target_id = '2305.08530'
paper_index = db.find_index_by_id(target_id)

knn_results = db.search_cosine_knn(db.embeddings[paper_index], k=5)
for r in knn_results:
    print(f"ID: {r[0]}, Score: {r[3]}, Title: {r[1]}")
    print("Abstract:", r[2])
    print("\n")
# === end of loading index and metadata === #

cursor.close()
conn.close()