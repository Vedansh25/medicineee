import streamlit as st
import pandas as pd
import mysql.connector
import subprocess

# Initialize the database
conn = mysql.connector.connect(
     host="user1.cbqcscyws2w5.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="123456789",
    port="3306",
    database="user1"
)
c = conn.cursor()

# Create the employees table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS employees
             (id INT PRIMARY KEY, name VARCHAR(255), position VARCHAR(255), email VARCHAR(255), phone VARCHAR(255))''')
conn.commit()

# Define functions to interact with the database
# Define the list of valid email domains
VALID_EMAIL_DOMAINS = ["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com"]

def add_employee(name, position, email, phone):
    if not all([name, position, email, phone]):
        st.warning("All fields are required")
        return
    if name.isalpha():
        if not any(email.endswith(domain) for domain in VALID_EMAIL_DOMAINS):
            st.warning("Invalid email address")
            return
        if not (phone.isdigit() and len(phone) == 10):
            st.warning("Invalid phone number")
            return
        c.execute("SELECT MAX(id) FROM employees")
        max_id = c.fetchone()[0] or 0
        new_id = max_id + 1
        c.execute("INSERT INTO employees (id, name, position, email, phone) VALUES (%s,%s,%s,%s,%s)", (new_id, name, position, email, phone))
        conn.commit()
        st.success(f"Added employee {name} with ID {new_id}")
    else:
        st.warning("Invalid name")

def view_employees():
    c.execute("SELECT * FROM employees")
    employees = c.fetchall()
    if not employees:
        st.warning("No employees found")
    else:
        df = pd.DataFrame(employees, columns=["ID", "Name", "Position", "Email", "Phone"])
        st.dataframe(df)

def delete_employee(id):
    c.execute("SELECT name FROM employees WHERE id=%s", (id,))
    employee_name = c.fetchone()
    if not employee_name:
        st.warning(f"No employee found with ID {id}")
    else:
        c.execute("DELETE FROM employees WHERE id=%s", (id,))
        conn.commit()
        st.success(f"Deleted employee {employee_name[0]} with ID {id}")

def search_employee(input_str):
    try:
        # Check if input is a valid integer ID
        id = int(input_str)
        c.execute("SELECT * FROM employees WHERE id=%s", (id,))
        employees = c.fetchall()
        if not employees:
            st.warning(f"No employee found with ID {id}")
        else:
            df = pd.DataFrame(employees, columns=["ID", "Name", "Position", "Email", "Phone"])
            st.dataframe(df)
            
    except ValueError:
        # Assume input is a name and search for employees whose names contain the input string
        c.execute("SELECT * FROM employees WHERE name LIKE %s", (f"%{input_str}%",))
        employees = c.fetchall()
        if not employees:
            st.warning(f"No employee found with name containing {input_str}")
        else:
            df = pd.DataFrame(employees, columns=["ID", "Name", "Position", "Email", "Phone"])
            st.dataframe(df)

# Define the Streamlit app
def app():
    # Add a logo to the header section
    st.image("https://img.freepik.com/free-vector/online-doctor-consultation-illustration_88138-414.jpg?size=626&ext=jpg", width=400)
    # Add custom styles to the sidebar
    st.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background-color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Add a title to the app
    st.title("Staff Management")
    
    # Define the menu options
    menu = ["Home", "View Employees", "Add Employee", "Delete Employee", "Search Employee","Back"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to the Medical Store Staff Management. Use the menu on the left to navigate.")

    elif choice == "View Employees":
        st.subheader("View Employees")
        view_employees()

    elif choice == "Add Employee":
        st.subheader("Add Employee")
        with st.form(key="add_employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name").strip()
                position = st.text_input("Position").strip()
            with col2:
                email = st.text_input("Email")
                phone = st.text_input("Phone")
            submit_button = st.form_submit_button(label="Add")

            if submit_button:
                add_employee(name, position, email, phone)

    elif choice == "Delete Employee":
        st.subheader("Delete Employee")
        id = st.number_input("Enter the ID of the employee to delete")
        if st.button("Delete"):
            delete_employee(id)

    elif choice == "Search Employee":
        st.subheader("Search Employee")
        input_str = st.text_input("Enter the ID or name of the employee").strip()
        if st.button("Search"):
            search_employee(input_str)

    elif choice == "Back":
        subprocess.run(["streamlit","run","interface2.py"])

# Run the app
if __name__ == "__main__":
    app()