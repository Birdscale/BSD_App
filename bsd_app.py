import streamlit as st
from PIL import Image
import db
from database import insert_user, authenticate

# Define session state class
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Function to create the signup form
def signup_form():
    st.header("User Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Signup", key="signup_button"):  # Add unique key
        if username and password:
            if insert_user(username, password):
                st.success("Signup successful! You can now login.")
            else:
                st.error("Failed to signup.")
        else:
            st.warning("Please enter both username and password.")

# Function to create the login form
def login_form():
    st.header("User Login")
    username = st.text_input("Username", key="login_username_input")  # Add unique key
    password = st.text_input("Password", type="password", key="login_password_input")  # Add unique key
    if st.button("Login", key="login_button"):  # Add unique key
        if username and password:
            if authenticate(username, password):
                st.session_state.logged_in = True  # Set logged_in state to True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password. Please try again.")
        else:
            st.warning("Please enter both username and password.")

# Load custom CSS for styling
def load_custom_css():
    custom_css = """
    <style>
    /* Add your custom CSS styles here */
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
    }
    .header {
        background-color: red;
        color: white;
        padding: 20px;
        text-align: center;
    }
    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        width: 250px;
        height: 100%;
        background-color: #f0f0f0;
        padding: 20px;
        overflow-y: auto;
    }
    .content {
        margin-left: 250px;
        padding: 20px;
    }
    .about-section {
        background-color: red;
        padding: 20px;
        margin-bottom: 20px;
    }
    .tab {
        display: inline-block;
        padding: 10px 20px;
        background-color: #005792;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin-right: 10px;
    }
    .tab:hover {
        background-color: #003d5a;
    }
    .tab.active {
        background-color: #003d5a;
    }
    @media only screen and (max-width: 768px) {
        .sidebar {
            width: 100%;
            height: auto;
            position: static;
        }
        .content {
            margin-left: 0;
        }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Function to load logo image
def load_logo():
    logo_path = "BSD_Logo.png"  # Update with your logo file path
    try:
        logo_image = Image.open(logo_path)
        return logo_image
    except Exception as e:
        st.error(f"Error loading logo image: {e}")
        return None

# Streamlit app
def main():
    load_custom_css()

    # Header
    st.markdown('<div class="header"><h1>BIRDSCALE</h1></div>', unsafe_allow_html=True)

    # Load logo
    logo_image = load_logo()
    if logo_image:
        st.sidebar.image(logo_image, use_column_width=False)
    else:
        st.sidebar.error("Logo image not found")

    # About Us section
    st.sidebar.markdown('## About Us')
    about_us_content = """
        WHO WE ARE 

    Going airborne
    to explore the world
    from the sky.
        """
    st.sidebar.write(about_us_content)

    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Show authentication buttons if not logged in
    if not st.session_state.logged_in:
        show_auth_buttons()
    else:
        show_navigation()

# Function to show authentication buttons
def show_auth_buttons():
    option = st.selectbox("Create a account", ["Login", "Signup"])
    if option == "Login":
        login_form()
    elif option == "Signup":
        signup_form()

# Function to show navigation options after successful login
def show_navigation():
    # Add tabs
    tabs = ["Create Project", "Upload Images", "Retrieve Images", "Logout"]  # Added logout option
    current_tab = st.sidebar.radio("Navigation", tabs)

    # Render the selected tab
    if current_tab == "Create Project":
        create_table_tab()
    elif current_tab == "Upload Images":
        upload_images_tab()
    elif current_tab == "Retrieve Images":
        retrieve_images_tab()
    elif current_tab == "Logout":
        st.session_state.logged_in = False  # Set logged_in state to False
        st.success("Logged out successfully!")
        show_auth_buttons()

# Create table tab
def create_table_tab():
    st.header("Create New Project")
    table_name = st.text_input("Enter Project name:")
    if st.button("Create Project"):
        if table_name:
            result = db.create_table(table_name)
            st.write(result)
        else:
            st.warning("Please enter a Project name.")

# Upload images tab
def upload_images_tab():
    st.header("Upload Images")
    table_name = st.text_input("Enter Project name:")
    uploaded_files = st.file_uploader("Upload multiple images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if st.button("Upload Images"):
        if table_name and uploaded_files:
            for file in uploaded_files:
                try:
                    filename = file.name
                    image_data = file.read()
                    result = db.upload_image(table_name, filename, image_data)
                    st.write(result)
                except Exception as e:
                    st.error(f"Error uploading image: {e}")

# Retrieve images tab
def retrieve_images_tab():
    st.header("Retrieve Images")
    table_name = st.selectbox("Select Project", db.get_all_tables())
    if st.button("Retrieve Images"):
        image_names = db.get_all_image_names(table_name)
        if image_names:
            zip_buffer = db.get_images_zip_buffer(table_name, image_names)
            if zip_buffer:
                st.download_button(label="Download Zip", data=zip_buffer, file_name=f"{table_name}_images.zip", mime="application/zip")
        else:
            st.info("No images found for the selected project.")

if __name__ == '__main__':
    db.create_users_table()  # Ensure users table exists
    main()
