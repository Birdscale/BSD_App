import psycopg2
from psycopg2 import sql
from io import BytesIO
import zipfile
import hashlib

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
def create_users_table():
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()

            # Create the users table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                              (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
            conn.commit()

            cursor.close()
            conn.close()
            print("Users table created successfully.")
        else:
            print("Database connection failed.")
    except psycopg2.Error as e:
        print(f"Error creating users table: {e}")


# Function to insert user details into the database
def insert_user(username, password):
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()

            # Check if the username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                print("Username already exists.")
                return False

            # Hash the password before storing it in the database
            hashed_password = hash_password(password)

            # Insert user details into the table
            insert_query = sql.SQL(
                "INSERT INTO users (username, password) VALUES (%s, %s)")
            cursor.execute(insert_query, (username, hashed_password))

            conn.commit()
            cursor.close()
            conn.close()

            print("User registered successfully.")
            return True
        else:
            print("Database connection failed.")
            return False
    except psycopg2.Error as e:
        print(f"Error registering user: {e}")
        return False

# Function to hash a password
def hash_password(password):
    # Hash the password using SHA-256 algorithm
    return hashlib.sha256(password.encode()).hexdigest()

# Function to authenticate user credentials
def authenticate(username, password):
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()

            # Retrieve the hashed password for the given username
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()

            if row:
                stored_password = row[0]
                # Check if the provided password matches the stored password
                if stored_password == hash_password(password):
                    print("User authenticated successfully.")
                    return True

            cursor.close()
            conn.close()
        else:
            print("Database connection failed.")
    except psycopg2.Error as e:
        print(f"Error authenticating user: {e}")
    return False

# Create users table on startup
create_users_table()
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
