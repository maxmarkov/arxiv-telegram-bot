import psycopg2
from psycopg2 import sql

def connect_to_postgres(database:str="postgres", user:str="postgres", password:str="", host:str= 'localhost', port:int=5432):
    """ Connects to a PostgreSQL database and returns the connection object.

    :param host: Hostname or IP address of the PostgreSQL server
    :param port: Port number on which PostgreSQL is running
    :param database: Name of the database to connect to
    :param user: Username for authentication
    :param password: Password for authentication
    :return: Connection object if successful, None otherwise
    """
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        print("Connected to the database successfully")
        return conn, cursor
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def check_id_and_insert(cursor, conn, table_name, data):
    """ Checks if an ID exists in the table, and if not, inserts a new row.
    
    :param cursor: The database cursor.
    :param conn: The database connection object.
    :param table_name: Name of the table to interact with.
    :param data: Dictionary containing the data to insert.
    """
    try:
        # Check if the ID exists
        cursor.execute(sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(table_name)), (data['id'],))

        result = cursor.fetchone()

        if result:
            print(f"Entry with ID {data['id']} already exists.")
        else:
            columns = data.keys()
            values = [data[column] for column in columns]
            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() * len(values))
            )
            cursor.execute(insert_query, values)
            conn.commit()
            print(f"Inserted new entry with ID {data['id']}.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()

def get_ids_not_in_database(input_ids, cursor, table_name):
    """ Retrieve IDs from the input list that are not present in the PostgreSQL database using a provided cursor.

    Args:
        input_ids (list): List of IDs to check.
        cursor (psycopg2.extensions.cursor): Database cursor to use for querying.

    Returns:
        list: List of IDs that are not in the database.
    """
    ids_not_in_database = []

    try:
        cursor.execute(f"SELECT id FROM {table_name} WHERE id = ANY(%s)", (input_ids,))
        existing_ids = set(row[0] for row in cursor.fetchall())
        ids_not_in_database = [id for id in input_ids if id not in existing_ids]

    except psycopg2.Error as e:
        print(f"Error: {e}")

    return ids_not_in_database