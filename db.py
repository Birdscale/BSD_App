# db.py

import psycopg2
from psycopg2 import sql
from io import BytesIO
import zipfile

# Define database connection parameters
dbname = "surya"
user = "postgres"
password = "Vijay@123"
host = "localhost"
port = "8501"

# Function to connect to the PostgreSQL database
def connect_to_database():
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn

# Function to create a new table
def create_table(table_name):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Create the table
        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} (id SERIAL PRIMARY KEY, name VARCHAR, data BYTEA)").format(sql.Identifier(table_name))
        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()

        return f"Table '{table_name}' created successfully."
    except Exception as e:
        return f"Error creating table: {e}"

# Function to upload an image to a table
def upload_image(table_name, filename, image_data):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Insert image data into the table
        insert_query = sql.SQL("INSERT INTO {} (name, data) VALUES (%s, %s)").format(sql.Identifier(table_name))
        cursor.execute(insert_query, (filename, psycopg2.Binary(image_data)))

        conn.commit()
        cursor.close()
        conn.close()

        return f"Image '{filename}' uploaded successfully to table '{table_name}'."
    except Exception as e:
        return f"Error uploading image: {e}"

# Function to retrieve all table names
def get_all_tables():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Retrieve all table names from the database
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return tables
    except Exception as e:
        return []

# Function to retrieve all image names from a table
def get_all_image_names(table_name):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # Retrieve all image names from the table
        cursor.execute(sql.SQL("SELECT name FROM {}").format(sql.Identifier(table_name)))
        names = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return names
    except Exception as e:
        return []

# Function to retrieve images as a zip buffer
def get_images_zip_buffer(table_name, image_names):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for name in image_names:
                cursor.execute(sql.SQL("SELECT data FROM {} WHERE name = %s").format(sql.Identifier(table_name)), (name,))
                row = cursor.fetchone()
                if row:
                    image_data = row[0]
                    zip_file.writestr(name, image_data)

        cursor.close()
        conn.close()

        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        return None
