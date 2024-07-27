import streamlit as st
import requests
from datetime import date
import jwt  # Make sure you have installed pyjwt using 'pip install pyjwt'

# Define the API base URLs
base_url = "https://medical-backend.azurewebsites.net/api/v1/auth"
publications_base_url = "https://medical-backend.azurewebsites.net/api/v1/publications"
me_base_url = "https://medical-backend.azurewebsites.net/api/v1/me"

# Function to register a new user
def register_user(email, password, first_name, last_name, date_of_birth):
    data = {
        "email": email,
        "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "dateOfBirth": date_of_birth.isoformat()  # Convert date to ISO format string
    }
    response = requests.post(f"{base_url}/register", json=data)
    if response.status_code == 201:
        try:
            return response.json()
        except ValueError:
            st.error(f"Failed to decode JSON response: {response.text}")
            return None
    else:
        st.error(f"Failed to register: {response.text}")
        return None

# Function to login a user
def login_user(email, password):
    data = {
        "email": email,
        "password": password,
    }
    response = requests.post(f"{base_url}/login", json=data)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error(f"Failed to decode JSON response: {response.text}")
            return None
    else:
        st.error(f"Failed to login: {response.text}")
        return None

# Function to get user profile
def get_profile(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(me_base_url, headers=headers)
    if response.status_code == 200:
        try:
            if response.text.strip() == "":
                st.error("Empty response from server")
                return None
            return response.json()
        except ValueError:
            st.error(f"Failed to decode JSON response: {response.text}")
            st.json(response.text)  # Debug response text
            return None
    else:
        st.error(f"Failed to fetch profile: {response.text}")
        return None

# Function to update user profile
def update_profile(token, email, first_name, last_name):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "email": email,
        "fullname": {
            "firstName": first_name,
            "lastName": last_name,
        }
    }
    response = requests.put(me_base_url, json=data, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error(f"Failed to decode JSON response: {response.text}")
            return None
    else:
        st.error(f"Failed to update profile: {response.text}")
        return None

# Function to get all publications
def get_publications(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(publications_base_url, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            st.error(f"Failed to decode JSON response: {response.text}")
            return None
    else:
        st.error(f"Failed to fetch publications: {response.text}")
        return None

# Function to create a new publication
def create_publication(token, title, content, sickness_type, files, user_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "title": title,
        "content": content,
        "sicknessType": sickness_type,
        "files": files,
        "user": user_id,  # Include user ID in the request
        "modifiedBy": [user_id]  # Include the user in modifiedBy field
    }
    response = requests.post(publications_base_url, json=data, headers=headers)
    if response.status_code == 201:
        try:
            return response.json()
        except ValueError:
            st.error(f"Failed to decode JSON response: {response.text}")
            return None
    else:
        st.error(f"Failed to create publication: {response.text}")
        return None

# Function to delete a publication
def delete_publication(token, pub_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.delete(f"{publications_base_url}/{pub_id}", headers=headers)
    if response.status_code == 204:
        return True
    else:
        st.error(f"Failed to delete publication: {response.text}")
        return False

# Initialize page state
if 'page' not in st.session_state:
    st.session_state['page'] = 'register'

if 'token' not in st.session_state:
    st.session_state['token'] = None

# Page navigation
def navigate_to(page):
    st.session_state['page'] = page

# Sidebar navigation
def sidebar():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Profile"):
        navigate_to('profile')
    if st.sidebar.button("Publications"):
        navigate_to('publications')
    if st.sidebar.button("Logout"):
        st.session_state['token'] = None
        navigate_to('login')

# Streamlit interface
def register_page():
    st.title("User Registration")
    st.markdown("### Please fill in your details to register")

    with st.form(key='register_form'):
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        first_name = st.text_input("First Name", key="register_first_name")
        last_name = st.text_input("Last Name", key="register_last_name")
        date_of_birth = st.date_input("Date of Birth", value=date.today(), min_value=date(1900, 1, 1), max_value=date.today(), key="register_date_of_birth")  # Set default date to today and define a range

        submit_button = st.form_submit_button(label='Register')
        if submit_button:
            user_data = register_user(email, password, first_name, last_name, date_of_birth)
            if user_data:
                st.success("User registered successfully!")
                navigate_to('login')

    st.markdown("### Already have an account?")
    if st.button("Go to Login", key="to_login"):
        navigate_to('login')

def login_page():
    st.title("User Login")
    st.markdown("### Please enter your login details")

    with st.form(key='login_form'):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        submit_button = st.form_submit_button(label='Login')
        if submit_button:
            login_data = login_user(email, password)
            if login_data:
                st.session_state['token'] = login_data['accessToken']
                st.success("Login successful!")
                navigate_to('profile')

    st.markdown("### Don't have an account?")
    if st.button("Go to Register", key="to_register"):
        navigate_to('register')

def profile_page():
    st.title("User Profile")
    token = st.session_state.get('token', None)

    if token:
        profile = get_profile(token)
        if profile:
            with st.form(key='profile_form'):
                email = st.text_input("Email", value=profile.get('email', ''), key="profile_email")
                first_name = st.text_input("First Name", value=profile.get('fullname', {}).get('firstName', ''), key="profile_first_name")
                last_name = st.text_input("Last Name", value=profile.get('fullname', {}).get('lastName', ''), key="profile_last_name")

                submit_button = st.form_submit_button(label='Update Profile')
                if submit_button:
                    updated_profile = update_profile(token, email, first_name, last_name)
                    if updated_profile:
                        st.success("Profile updated successfully!")
                        navigate_to('profile')

            if st.button("Go to Publications", key="to_publications"):
                navigate_to('publications')

    else:
        st.error("User not logged in")
        navigate_to('login')

def publications_page():
    st.title("Publications")
    token = st.session_state.get('token', None)
    
    if token:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        user_id = decoded_token.get('_id', None)

        if not user_id:
            st.error("Failed to decode user ID from token")
            return

        publications = get_publications(token)
        if publications:
            for pub in publications:
                with st.expander(pub['title']):
                    st.write(pub['content'])
                    st.write(f"Sickness Type: {pub['sicknessType']}")
                    st.write(f"Files: {', '.join(pub['files'])}")
                    if st.button(f"Delete {pub['title']}", key=f"delete_{pub['_id']}"):
                        delete_publication(token, pub['_id'])
                        st.experimental_rerun()  # Ensure the page updates immediately

        st.header("Create New Publication")
        with st.form(key='create_pub_form'):
            title = st.text_input("Title", key="pub_title")
            content = st.text_area("Content", key="pub_content")
            sickness_type = st.text_input("Sickness Type", key="pub_sickness_type")
            files = st.text_input("Files (comma-separated URLs)", key="pub_files").split(',')

            submit_button = st.form_submit_button(label='Create Publication')
            if submit_button:
                new_pub = create_publication(token, title, content, sickness_type, files, user_id)
                if new_pub:
                    st.success("Publication created successfully!")
                    st.json(new_pub)
                    st.experimental_rerun()  # Ensure the page updates immediately

    else:
        st.error("User not logged in")
        navigate_to('login')

# Render the appropriate page
if 'rerun' in st.session_state and st.session_state['rerun']:
    st.session_state['rerun'] = False
    st.experimental_rerun()

if st.session_state['token']:
    sidebar()
    if st.session_state['page'] == 'profile':
        profile_page()
    elif st.session_state['page'] == 'publications':
        publications_page()
else:
    if st.session_state['page'] == 'register':
        register_page()
    elif st.session_state['page'] == 'login':
        login_page()

# Custom CSS styling with animations
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.3s, transform 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stTextInput>div>input, .stDateInput>div, .stTextArea>div>textarea {
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    .stTextInput>div>input:focus, .stDateInput>div:focus, .stTextArea>div>textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.6);
    }
    .stFormSubmitButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.3s, transform 0.3s;
    }
    .stFormSubmitButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)
