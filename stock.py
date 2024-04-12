import streamlit as st
import mysql.connector
from datetime import date
import pandas as pd
import subprocess

# Connect to MySQL database
mydb = mysql.connector.connect(
     host="user1.cbqcscyws2w5.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="123456789",
    port="3306",
    database="user1"
)

# Check if the table exists, and create it if it doesn't
mycursor = mydb.cursor()
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INT AUTO_INCREMENT PRIMARY KEY,
        refno VARCHAR(255),
        name VARCHAR(255),
        types VARCHAR(255),
        company VARCHAR(255),
        uses VARCHAR(255),
        mfgdate DATE,
        expdate DATE,
        salt VARCHAR(255),
        quantity INT,
        price FLOAT
    )
""")


# Functions for adding, updating, deleting, showing, and searching medicines

def add_medicine(refno, name, types, company, uses, mfgdate, expdate, salt, quantity, price):
    sql = "INSERT INTO medicines (refno, name, types, company, uses, mfgdate, expdate, salt, quantity, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (refno, name, types, company, uses, mfgdate, expdate, salt, quantity, price)
    mycursor.execute(sql, val)
    mydb.commit()

def update_medicine():
    # Fetch the last added medicine from the database
    mycursor.execute("SELECT * FROM medicines ORDER BY id DESC LIMIT 1")
    last_added_medicine = mycursor.fetchone()
    medicine = None

    # Create a dropdown menu with the reference numbers of all medicines
    mycursor.execute("SELECT refno FROM medicines")
    reference_numbers = [row[0] for row in mycursor.fetchall()]
    selected_refno = st.selectbox("Select reference number:", reference_numbers)

    # Set the default values in the form
    types_dict = {"Ayurvedic": 1, "Anti Bacterial": 2, "Baby Product": 3, "Capsule": 4, "First Aid": 5, "Gloves": 6, "Gown": 7, "Health Care Equipment": 8, "Injection": 9, "Tablet": 10, "Skin Care": 11, "Syrup": 12}
    types = list(types_dict.keys())[0]  # set default value
    if last_added_medicine is not None and selected_refno == last_added_medicine[1]:
        name = st.text_input("Name", value=medicine[2] if medicine is not None else "")
        medicine_types = list(types_dict.keys())
        if last_added_medicine[3] in medicine_types:
            index_value = medicine_types.index(last_added_medicine[3])
        else:
            index_value = 0
        types = st.selectbox("Type", medicine_types, index=index_value)
        company = st.text_input("Company", value=last_added_medicine[4])
        uses = st.text_input("Uses", value=last_added_medicine[5])
        mfgdate = st.date_input("Manufacturing Date", value=last_added_medicine[6])
        expdate = st.date_input("Expiry Date", value=last_added_medicine[7])
        salt = st.text_input("Salt", value=last_added_medicine[8])
        quantity = st.number_input("Quantity", value=last_added_medicine[9], min_value=0)
        price = st.number_input("Price", value=int(last_added_medicine[10]), min_value=0)
    else:
        # Fetch the selected medicine from the database
        query = f"SELECT * FROM medicines WHERE refno = '{selected_refno}'"
        mycursor.execute(query)
        medicine = mycursor.fetchone()

        # Set the default values in the form
        name = st.text_input("Name", value=medicine[2] if medicine is not None else "")        
        company = st.text_input("Company", value=medicine[4] if medicine is not None else "")
        uses = st.text_input("Uses", value=medicine[5] if medicine is not None else "")
        mfgdate = st.date_input("Manufacturing Date", value=medicine[6] if medicine is not None else None)
        expdate = st.date_input("Expiry Date", value=medicine[7] if medicine is not None else None)
        salt = st.text_input("Salt", value=medicine[8] if medicine is not None else "")
        quantity = st.number_input("Quantity", value=medicine[9] if medicine is not None else 0, min_value=0)
        price = st.number_input("Price", value=int(medicine[10]) if medicine is not None else 0, min_value=0)
        
        if medicine is not None and medicine[3] in types_dict.values():
            types = list(types_dict.keys())[list(types_dict.values()).index(medicine[3])]

    # Update the selected medicine in the database
    if st.button("Update"):
        types_val = types_dict[types]
        query = f"UPDATE medicines SET name = '{name}', types = {types_val}, company = '{company}', uses = '{uses}', mfgdate = '{mfgdate}', expdate = '{expdate}', salt = '{salt}', quantity = {quantity}, price = {price} WHERE refno = '{selected_refno}'"
        mycursor.execute(query)
        mydb.commit()
        st.success("Medicine updated successfully!")
        
def delete_medicine(refno):
    sql = "DELETE FROM medicines WHERE refno = %s"
    val = (refno,)
    mycursor.execute(sql, val)
    mydb.commit()
    st.success("Medicine deleted successfully!")


def show_medicines():
    hide_index_css = """
    <style>
        .dataframe tbody tr th:first-child,
        .dataframe tbody tr td:first-child {
            display: none;
        }
    </style>"""
    st.markdown(hide_index_css, unsafe_allow_html=True)
    mycursor.execute("SELECT refno,name, types, company, uses, mfgdate, expdate, salt, quantity, price FROM medicines")
    columns = [desc[0] for desc in mycursor.description]
    medicines = mycursor.fetchall()
    if len(medicines) == 0:
        st.warning("No medicines found!")
    else:
        medicines_df = pd.DataFrame(list(medicines), columns=columns)
        hide_index_css = """<style>.dataframe tbody tr th:first-child,.dataframe tbody tr td:first-child {display: none;}</style>"""
        st.markdown(hide_index_css, unsafe_allow_html=True)
        st.dataframe(medicines_df)
        
def search_medicine(search_by, search_query):
    if search_query:
        if search_by == "Name":
            query = f"SELECT refno, name, types, company, uses, mfgdate, expdate, salt, quantity, price FROM medicines WHERE name LIKE '%{search_query}%'"
        elif search_by == "Company":
            query = f"SELECT refno, name, types, company, uses, mfgdate, expdate, salt, quantity, price FROM medicines WHERE company LIKE '%{search_query}%'"
        mycursor.execute(query)
        medicines = mycursor.fetchall()
        if len(medicines) == 0:
            st.warning("No medicines found!")
        else:
            columns = [desc[0] for desc in mycursor.description]
            medicines_with_columns = [columns] + list(medicines)
            st.table(medicines_with_columns)

# Define Streamlit app
def app():
    # Add a logo to the header section
    st.image("https://img.freepik.com/free-photo/closeup-view-pharmacist-hand-taking-medicine-box-from-shelf-drug-store_342744-320.jpg?w=360", width=400)
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

    st.title("Medicine Inventory")
    menu = ["Home","Add Medicine", "Update Medicine", "Delete Medicine", "View Medicines", "Search Medicine","Back"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Home":
        st.subheader("Home")
        st.write("Welcome to the Medical Store Inventory. Use the menu on the left to navigate.")

    if choice == "Add Medicine":
        try:
    # Get the next auto-incremented ID from the database
            mycursor.execute("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'medicine_inventory' AND TABLE_NAME = 'medicines'")
            next_id_row = mycursor.fetchone()
            if next_id_row is not None:
                next_id = next_id_row[0]
            else:
                next_id = None
                st.error("Error fetching next ID: No rows returned.")

            # Display the ID value in a non-editable text input
            refno = st.text_input("Ref No", value=str(next_id), key="id", disabled=True)

            name = st.text_input("Name", max_chars=30).strip()
            types = st.selectbox("Type", ["Ayurvedic", "Anti Bacterial", "Baby Product", "Capsule", "First Aid","Gloves", "Gown",  "Health Care Equipment","Injection", "Tablet", "Skin Care","Syrup"])
            company = st.text_input("Company", max_chars=30).strip()
            uses = st.text_area("Usage").strip()
            mfgdate = st.date_input("Manufacturing Date", max_value=date.today())
            expdate = st.date_input("Expiry Date", min_value=mfgdate)
            
            # Options for the selectbox
            salt_option = ["Aspirin","Atovastatin","Amoxicillin","Ciprofloacin","Losartan","Metformin","Paracetamol","Other"]
            
            # Display the selectbox and text input
            salt = st.selectbox("Salt", salt_option)
            if salt == "Other":
                other_salt = st.text_input("Enter Salt name").strip()
                salt = other_salt
            quantity = st.number_input("Quantity", min_value=1)
            price = st.number_input("Price", min_value=1, step=None)
            
            if st.button("Add"):
                if name=="" and company=="" and uses=="" and price=="":
                    st.error("All fields are required")
                else:
                    try:
                        add_medicine(refno, name, types, company, uses, mfgdate, expdate, salt, quantity, price)
                        st.session_state.success_message = "Medicine added successfully"
                    except Exception as e:
                        st.error("Error adding medicine: {}".format(str(e)))

                    if "success_message" in st.session_state:
                        st.success(st.session_state.success_message)
                        del st.session_state.success_message
        except Exception as e:
            st.error(f"Error fetching next ID: {e}")


    elif choice == "Update Medicine":
        update_medicine()

    elif choice == "Delete Medicine":
        refno = st.text_input("Delete medicine by")
        if st.button("Delete"):
            delete_medicine(refno)

    elif choice == "View Medicines":
        show_medicines()

    elif choice == "Search Medicine":
        search_by = st.selectbox("Search medicine by:", ["Name", "Company"])
        search_query = st.text_input(f"Search medicine by {search_by.lower()}:", max_chars=30).strip()
        if st.button("Search"):
            search_medicine(search_by, search_query)

    elif choice == "Back":
        subprocess.run(["streamlit", "run", "interface2.py"])
        

if __name__ == '__main__':
    app()
