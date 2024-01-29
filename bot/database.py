import os
import logging
import psycopg2
from psycopg2 import sql
from typing import Optional, List, Tuple

import psycopg2
from psycopg2 import sql
import logging

class PostgresHandler:
    """ A class for interacting with a PostgreSQL database. """
    def __init__(self, database="postgres", user="postgres", password="", host='localhost', port=5432, table_name="arxiv_articles"):
        """ Initialize the PostgresHandler object with database connection details.
        """
        if not self.check_env_variables():
            logging.error("Missing required environment variables.")
            raise EnvironmentError("Missing required environment variables.")
 
        self.conn, self.cursor = self.connect_to_postgres()
        if self.conn is None or self.cursor is None:
            raise Exception("Could not connect to the database.")

    def check_env_variables(self):
        """ Checks if required environment variables are set. """
        required_env_vars = ['POSTGRES_DB', 'POSTGRES_USERNAME', 'POSTGRES_PASSWORD', 'POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_TABLE']
        all_vars_present = True

        for var in required_env_vars:
            if not os.getenv(var):
                logging.error(f"Environment variable {var} is not set.")
                all_vars_present = False

        return all_vars_present

    def connect_to_postgres(self):
        """ Connects to a PostgreSQL database and returns the connection and cursor objects.
        """
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT'),
                database=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USERNAME'),
                password=os.getenv('POSTGRES_PASSWORD')
            )
            cursor = conn.cursor()
            logging.info("Connected to the database successfully")
            return conn, cursor
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None, None

    def close_connection(self):
        """ Close the database cursor and connection. """
        if self.cursor is not None:
            self.cursor.close()
            logging.info("Database cursor closed.")

        if self.conn is not None:
            self.conn.close()
            logging.info("Database connection closed.")

    def get_ids_not_in_database(self, input_ids: List[str], batch_size:int=1000) -> List[str]:
        """ Retrieve IDs from the input list that are not present in the PostgreSQL database.
        Args:
            input_ids (list): List of IDs to check.
            batch_size (int): The size of each batch to query (default: 1000).
        Returns:
            list: List of IDs that are not in the database.
        """
        ids_not_in_database = set(input_ids)
        try:
            for i in range(0, len(input_ids), batch_size):
                batch_ids = input_ids[i:i+batch_size]
                query = sql.SQL("SELECT id FROM {} WHERE id = ANY(%s)").format(sql.Identifier(os.getenv('POSTGRES_TABLE')))
                self.cursor.execute(query, (batch_ids,))
                existing_ids = set(row[0] for row in self.cursor.fetchall())
                ids_not_in_database.difference_update(existing_ids)

        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            raise

        return list(ids_not_in_database)
    
    def select_metadata(self, metadata: dict):
        """ Selects metadata of articles with IDs not present in the database.
        Args:
            metadata (dict): Dictionary containing the metadata of articles.
        Returns:
            dict: Dictionary containing the metadata of articles with IDs not present in the database.
        """
        ids = [item['id'] for item in metadata]
        ids_selected= self.get_ids_not_in_database(ids)
        if ids_selected:
            logging.info(f"{len(ids_selected)} articles to be submitted: {ids_selected}")
            metadata_selected = [item for item in metadata if item['id'] in ids_selected]
            return metadata_selected
        else:
            logging.info(f"No new articles have been found.\n")
            return None

    def check_id_and_insert(self, data:dict):
        """ Checks if an ID exists in the table, and if not, inserts a new row.
        Args:
            data (dict): A dictionary containing the data to insert.
        Returns:
            None
        """
        try:
            # Check if the ID exists
            self.cursor.execute(sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(os.getenv('POSTGRES_TABLE'))), (data['id'],))
            result = self.cursor.fetchone()

            if result:
                logging.info(f"Entry with ID {data['id']} already exists.")
            else:
                columns = data.keys()
                values = [data[column] for column in columns]
                insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                    sql.Identifier(os.getenv('POSTGRES_TABLE')),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(sql.Placeholder() * len(values))
                )
                self.cursor.execute(insert_query, values)
                self.conn.commit()
                logging.info(f"Inserted new entry with ID {data['id']}.")
                
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            self.conn.rollback()

    def retrieve_rows(self, n: Optional[int] = None) -> Optional[List[Tuple]]:
        """ Retrieve rows from a PostgreSQL table.
        Args:
            n (Optional[int]): The number of rows to retrieve. If None, retrieves all rows.
        Returns:
            Optional[List[Tuple]]: A list of tuples containing the retrieved rows, or None if an error occurs.
        """
        try:
            query = sql.SQL("SELECT id, title, summary FROM {} {}").format(
                sql.Identifier(os.getenv('POSTGRES_TABLE')),
                sql.SQL("LIMIT %s") if n is not None else sql.SQL("")
            )
            self.cursor.execute(query, (n,) if n is not None else None)
            rows = self.cursor.fetchall()
            logging.info(f"Retrieved {len(rows)} rows from the database.")
            return rows

        except psycopg2.Error as e:
            logging.error(f"Error: {e}")
            return None