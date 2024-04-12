import streamlit as st
import mysql.connector
import re
from PIL import Image
import urllib.request
import subprocess

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="user1.cbqcscyws2w5.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="123456789",
    port="3306",
    database="user1"
)
mycursor = mydb.cursor()

# Load the image file from URL
with urllib.request.urlopen("https://t4.ftcdn.net/jpg/02/74/73/01/360_F_274730109_gF0azWfAPbZFLr06yKbFu8S5CPSNMYJs.jpg") as url:
    image = Image.open(url)

# Create users table if it doesn't exist
mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255), password VARCHAR(255), company_name VARCHAR(255))")

# Define function to validate password
def validate_password(password, confirm_password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if password != confirm_password:
        return False
    return True

#Function to check user already exist
def user_exists(email):
    mycursor.execute("SELECT * FROM users WHERE email=%(email)s", {"email": email})
    result = mycursor.fetchone()
    if result:
        return True
    else:
        return False

# Define function to validate email
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
def validate_email(email):
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

# Set up Streamlit app
st.set_page_config(page_title="Login/Sign up")
st.title("Medical Store Management System")

page = st.sidebar.radio("Select action:", ("Login", "Sign up"))

if page == "Login":
    st.title("Login")

    # Get user inputs
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Check if user exists in database
    def authenticate(email, password):
        mycursor.execute("SELECT * FROM users WHERE email=%(email)s AND password=%(password)s", {"email": email, "password": password})
        result = mycursor.fetchone()
        if result:
            return True
        else:
            return False

    # Validate inputs and authenticate user
    if st.button("Login"):
        if authenticate(email, password):
            st.success("You have successfully logged in!")
            subprocess.run(["streamlit","run","interface2.py"])
        else:
            st.error("Incorrect email or password. Please try again.")


else:
    st.title("Sign up")

    # Get user inputs
    email = st.text_input("Email")
    password = st.text_input("Password", type="password",max_chars=20)
    confirm_password = st.text_input("Confirm password", type="password")
    company_name = st.text_input("Company name",max_chars=30).strip()

    # Validate inputs and create user in database
    if st.button("Sign up"):
        if not validate_email(email):
            st.error("Please enter a valid email address.")
        else:
            password_message = validate_password(password, confirm_password)
            if password_message == True:
                if company_name=="":
                    st.error("Company Name should not be empty")
                elif user_exists(email):
                    st.error("This user already exists. Please log in.")
                else:
                    # Insert user into database
                    sql = "INSERT INTO users (email, password, company_name) VALUES (%s, %s, %s)"
                    val = (email, password, company_name)
                    mycursor.execute(sql, val)
                    mydb.commit()
                    st.success("You have successfully signed up!")
                    st.markdown("Already have an account? [Login here](/login)")

        st.sidebar.markdown("Already have an account? [Login here](/login)")

    # Display the image
st.image(image, use_column_width=True)