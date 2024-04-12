import streamlit as st
import pandas as pd
import mysql.connector
import uuid
import PyPDF2
import os
import webbrowser
from fpdf import FPDF
import subprocess


# Connect to MySQL server
connection = mysql.connector.connect(
     host="user1.cbqcscyws2w5.ap-south-1.rds.amazonaws.com",
    user="admin",
    password="123456789",
    port="3306",
    database="user1"
)
cursor = connection.cursor()
cursor.execute("SHOW TABLES LIKE 'bill'")
table_exists = cursor.fetchone()
if not table_exists:
    cursor.execute("""
        CREATE TABLE bill (
            id VARCHAR(255) PRIMARY KEY,
            item_name VARCHAR(255),
            quantity INT,
            price FLOAT,
            total_amount FLOAT,
            customer_name VARCHAR(255),
            mobile_number VARCHAR(255),
            mode_of_payment VARCHAR(255)
        )
    """)
    connection.commit()
cursor.close()

# Define function to fetch item names from database
def fetch_item_names():
    cursor = connection.cursor()
    sql = "SELECT DISTINCT name FROM medicines"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return [item[0] for item in result]

# Define function to fetch item details from database
def fetch_item_details(item_name):
    cursor = connection.cursor()
    sql = "SELECT name, company, price, quantity, expdate FROM medicines WHERE name = %s"
    cursor.execute(sql, (item_name,))
    result = cursor.fetchone()
    cursor.fetchall()  # Consume any remaining results
    cursor.close()
    return result

# Define function to save bill data to database
def save_bill_data(item_list, total_amount, customer_name, mobile_number, mode_of_payment, reference_number):
    cursor = connection.cursor()
    sql = "INSERT INTO bill (id, item_name, quantity, price, total_amount, customer_name, mobile_number, mode_of_payment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    for item in item_list:
        cursor.execute(sql, (reference_number, item['name'], item['quantity'], item['price'], item['total'], customer_name, mobile_number, mode_of_payment))
    connection.commit()
    cursor.close()


# Define function to generate bill PDF
def generate_pdf(bills, customer_name, mode_of_payment):
    pdf_filename = f"{customer_name}.pdf"
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(0, 10, "Bills Report", align='C', ln=1)
    pdf.set_font("Arial", size=12)

    # Customer details
    # Table header
    # Table header
    header = ['ID', 'Name', 'Mobile', 'Total', 'Payment', 'Item Name', 'Quantity', 'MRP']
    col_widths = [pdf.get_string_width(str(max(header, key=lambda x: len(str(x))))) + 6 for _ in range(len(header))]

    # Table data
    data = []
    for bill in bills:
        item_name = bill[5]
        item_details = fetch_item_details(item_name)
        if len(bill) > 6:
            quantity = bill[6]
        else:
            quantity = ''
        row = [bill[0], bill[1], bill[2], bill[3], bill[4], item_name, quantity, item_details[2]]
        data.append(row)



    # Calculate column widths based on maximum width of data in each column
    for row in data:
        for i in range(len(row)):
            col_width = pdf.get_string_width(str(row[i])) + 6
            if col_width > col_widths[i]:
                col_widths[i] = col_width

    # Scale table to fit page if necessary
    table_width = sum(col_widths)
    page_width = pdf.w - 2 * pdf.l_margin
    if table_width > page_width:
        st.warning("The table is too wide to fit on one page. The table will be scaled to fit the page.")
        scale_factor = page_width / table_width
        col_widths = [int(col_width * scale_factor) for col_width in col_widths]

    # Table header
    for i in range(len(header)):
        pdf.cell(col_widths[i], 10, header[i], border=1)
    pdf.ln()

    # Table data
    for row in data:
        row_heights = []
        for i in range(len(row)):
            cell_height = pdf.font_size + 2
            row_heights.append(cell_height)
            pdf.cell(col_widths[i], cell_height, str(row[i]), border=1)
        max_row_height = max(row_heights)
        for i in range(len(row)):
            if row_heights[i] < max_row_height:
                pdf.cell(col_widths[i], max_row_height - row_heights[i], '', border=1)
        pdf.ln()

    pdf.output(pdf_filename)

    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name=pdf_filename,
        mime="application/pdf"
    )

# Define function to generate bill
# Define function to generate bill
def generate_bill():
    # Get inputs from user
    customer_name = st.text_input("Enter customer name:")
    mobile_number = st.text_input("Enter mobile number:")
    item_names = fetch_item_names()
    selected_items = []
    for item_name in item_names:
        if st.checkbox(item_name):
            item_details = fetch_item_details(item_name)
            quantity = st.number_input(f"Enter quantity for {item_name}:", value=1, min_value=1)
            item_price = item_details[2]
            total_amount = item_price * quantity
            selected_items.append({"name": item_name, "quantity": quantity, "price": item_price, "total": total_amount})
    mode_of_payment = st.selectbox("Select mode of payment:", ["Cash", "Card"])

    # Get reference number from user
    reference_number_option = st.radio("Choose reference number option:", ["Sequential", "Custom"])
    if reference_number_option == "Sequential":
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM bill")
        count = cursor.fetchone()[0] + 1
        reference_number = str(count)
    else:
        reference_number = st.text_input("Enter reference number:")

    # Display selected items and total amount to user
    st.write("Selected items:")
    for item in selected_items:
        st.write("Item name:", item['name'])
        st.write("Company:", item_details[1])
        st.write("Price per unit:", item['price'])
        st.write("Quantity:", item['quantity'])
        st.write("Total amount:", item['total'])

    total_amount = sum([item['total'] for item in selected_items])

    # Add a button to save bill data to database
    if st.button("Save Bill"):
        if not customer_name:
            st.warning("Customer name cannot be empty.")
            return
        if not mobile_number.isdigit():
            st.warning("Mobile number should contain only digits.")
            return
        # Check if reference number already exists
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM bill WHERE id = %s", (reference_number,))
        existing_reference = cursor.fetchone()
        if existing_reference:
            st.warning("Reference number already exists. Please choose a different one.")
            return
        save_bill_data(selected_items, total_amount, customer_name, mobile_number, mode_of_payment, reference_number)
        st.success("Bill data saved to database.")



def view_bills():
    cursor = connection.cursor()
    sql = "SELECT id, customer_name, mobile_number, total_amount, mode_of_payment, item_name, quantity FROM bill"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    if len(result) == 0:
        st.write("No bills found.")
    else:
        df = pd.DataFrame(result, columns=["ID", "Customer Name", "Mobile Number", "Total Amount", "Mode of Payment", "Item Name", "Quantity"])
        st.dataframe(df)
        if st.button("Generate PDF"):
            mode_of_payment = result[0][4]
            generate_pdf(result, "Bills", mode_of_payment)
            st.success("PDF generated successfully.")


# Define function to delete bill
def delete_bill():
    bill_id = st.text_input("Enter bill ID:")
    if st.button("Delete bill"):
        cursor = connection.cursor()
        sql = "DELETE FROM bill WHERE id = %s"
        cursor.execute(sql, (bill_id,))
        connection.commit()
        cursor.close()
        st.write("Bill deleted successfully.")

# Define app
def app():
    st.title("Medical Store Management System")
    menu = ["Generate Bill", "View Bills", "Delete Bill", "Back"]
    choice = st.sidebar.selectbox("Select an option:", menu)
    if choice == "Generate Bill":
        generate_bill()
    elif choice == "View Bills":
        view_bills()
    elif choice == "Delete Bill":
        delete_bill()
    elif choice == "Back":
        subprocess.run(["streamlit","run","interface2.py"])

if __name__ == "__main__":
    app()
