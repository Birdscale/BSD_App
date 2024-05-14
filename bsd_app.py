import streamlit as st
import db
from PIL import Image
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
        background-color: #005792;
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
        background-color: #f0f0f0;
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

    # Add tabs
    tabs = ["Create Project", "Upload Images", "Retrieve Images"]
    current_tab = st.sidebar.radio("Navigation", tabs)

    # Render the selected tab
    if current_tab == "Create Project":
        create_table_tab()
    elif current_tab == "Upload Images":
        upload_images_tab()
    elif current_tab == "Retrieve Images":
        retrieve_images_tab()

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
                filename = file.name
                image_data = file.read()
                result = db.upload_image(table_name, filename, image_data)
                st.write(result)
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
    main()
