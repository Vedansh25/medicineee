import streamlit as st
import subprocess

# Set the page title and favicon
st.set_page_config(page_title="Medical Store Management System", page_icon=":pill:")

# Define the menu options
menu = ["Home","Stock Management", "Staff Management", "Bill Generation", "Back"]

# Add the menu to the sidebar
choice = st.sidebar.selectbox("Select an option", menu)

if choice == "Stock Management":
    subprocess.run(["streamlit","run","stock.py"])
    
elif choice == "Staff Management":
    subprocess.run(["streamlit","run","Staff Management.py"])
    
elif choice == "Bill Generation":
    subprocess.run(["streamlit","run","checking2.py"])
    

# Define the welcome message
st.write("# Medical Store Management System")
st.write("Welcome to our app! Use the menu on the left to navigate.")

# Add an image to the main screen
img_url = "https://media.istockphoto.com/id/1173932221/vector/man-pharmacist-stands-near-the-shelves-with-medicines-and-one-buyer-buy-pills-sale-of.jpg?s=612x612&w=0&k=20&c=LVDRdq622-tiLSUFGGjyipQ3k6s4mubNJzD_i3638Tc="
st.image(img_url, use_column_width=True)
