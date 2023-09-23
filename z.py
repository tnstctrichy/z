import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import csv
from prettytable import PrettyTable

st.set_page_config(layout="wide")

# Connect to the SQLite database
con = sqlite3.connect('stock_db.db')

# Define title and footer variables
st.title("Tnstc(kum)ltd., Trichy Region - Computer Stock Details")
st.write("Date:", datetime.now().strftime('%Y-%m-%d'))

footer = "\n\n\n    Asst.                   Supdt.                    B.M."

def export_data_to_csv(data, headers, file_name_prefix):
    try:
        # Generate the file name with date and search term
        file_extension = 'csv'
        date_string = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"{file_name_prefix}_{date_string}.{file_extension}"

        if os.path.exists(file_name):
            st.warning("File with the same name already exists. Please choose a different name.")
        else:
            with open(file_name, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(headers)
                for row in data:
                    csv_writer.writerow(row)
            st.success(f"Data exported to {file_name}")
    except Exception as e:
        st.error(f"Export error: {e}")

# Implement data manipulation functions
def insert(Depot, Location, Item, Make, Configuration, Serial_number, Remarks):
    res = con.cursor()
    sql = "INSERT INTO peripherals(Depot, Location, Item, Make, Configuration, Serial_number, Remarks) VALUES (?,?,?,?,?,?,?)"

    # Check if any of the mandatory fields are empty
    if not (Depot and Location and Item):
        st.error("Error: Depot, Location, and Item fields are mandatory.")
        return

    peripherals = (Depot, Location, Item, Make, Configuration, Serial_number, Remarks)
    res.execute(sql, peripherals)
    con.commit()
    st.success("Data Insert Success")

def update(Id):
    res = con.cursor()
    sql = "SELECT Depot, Location, Item, Make, Configuration, Serial_number, Remarks FROM peripherals WHERE id=?"
    res.execute(sql, (Id,))
    result = res.fetchone()
    if result:
        headers = ["Depot", "Location", "Item", "Make", "Configuration", "Serial_number", "Remarks"]
        table = PrettyTable(headers)
        table.add_row(result)
        st.write(table)

        Depot = st.text_input("Enter Depot (Leave blank to keep existing value): ", result[0])
        Location = st.text_input("Enter Location (Leave blank to keep existing value): ", result[1])
        Item = st.text_input("Enter Item (Leave blank to keep existing value): ", result[2])
        Make = st.text_input("Enter Make (Leave blank to keep existing value): ", result[3])
        Configuration = st.text_input("Enter Configuration (Leave blank to keep existing value): ", result[4])
        Serial_number = st.text_input("Enter Serial_number (Leave blank to keep existing value): ", result[5])
        Remarks = st.text_input("Enter Remarks (Leave blank to keep existing value): ", result[6])

        if st.button("Update Data"):
            sql = "UPDATE peripherals SET Depot=?, Location=?, Item=?, Make=?, Configuration=?, Serial_number=?, Remarks=? WHERE id=?"
            peripherals = (Depot, Location, Item, Make, Configuration, Serial_number, Remarks, Id)
            res.execute(sql, peripherals)
            con.commit()
            st.success("Data Update Success")
    else:
        st.error("No record found with the given ID.")

def search(term, sort_by_location=False):
    res = con.cursor()
    if not term.strip():
        sql = "SELECT id, Depot, Location, Item, Make, Configuration, Serial_number, Remarks FROM peripherals"
        file_name_prefix = "all_data"
        search_term = "all_data"
        if sort_by_location:
            sql += " ORDER BY Location ASC"  # Sort by Location in ascending order
        res.execute(sql)
    else:
        sql = f"SELECT id, Depot, Location, Item, Make, Configuration, Serial_number, Remarks FROM peripherals WHERE"
        sql += " Depot LIKE ? OR Location LIKE ? OR Item LIKE ? OR Serial_number LIKE ? OR Remarks LIKE ?"
        search_term = term.lower()
        if sort_by_location:
            sql += " ORDER BY Location ASC"  # Sort by Location in ascending order
        res.execute(sql, (f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%"))
        file_name_prefix = search_term

    result = res.fetchall()
    headers = ["sl.no", "Id", "Depot", "Location", "Item", "Make", "Configuration", "Serial_number", "Remarks"]

    table_data = []
    for index, row in enumerate(result, start=1):
        table_data.append([index] + list(row))

    return table_data, headers, file_name_prefix, search_term

def view_data():
    res = con.cursor()
    sql = "SELECT id, Depot, Location, Item, Make, Configuration, Serial_number, Remarks FROM peripherals"
    res.execute(sql)
    result = res.fetchall()
    headers = ["sl.no", "Id", "Depot", "Location", "Item", "Make", "Configuration", "Serial_number", "Remarks"]
    table_data = []

    # Prepare data for display
    for index, row in enumerate(result, start=1):
        table_data.append([index] + list(row))

    return table_data, headers

def delete(Id):
    res = con.cursor()
    sql = "SELECT Depot, Location, Item, Make, Configuration, Serial_number, Remarks FROM peripherals WHERE id=?"
    res.execute(sql, (Id,))
    result = res.fetchone()
    if result:
        headers = ["Depot", "Location", "Item", "Make", "Configuration", "Serial_number", "Remarks"]
        table = PrettyTable(headers)
        table.add_row(result)
        st.write(table)

        confirm = st.radio("Are you sure you want to delete this record?", ("Yes", "No"))
        if confirm == "Yes":
            sql = "DELETE FROM peripherals WHERE id=?"
            peripherals = (Id,)
            res.execute(sql, peripherals)
            con.commit()
            st.success("Data Delete Success")
        else:
            st.warning("Delete operation canceled.")
    else:
        st.error("No record found with the given ID.")

# Main Streamlit App
st.sidebar.title("Menu")
menu_choice = st.sidebar.selectbox("Select an Option", ["Home", "Add New Data", "Update Existing Data", "Delete Data", "Search Data", "View Data", "Export Search Results as Text"])

if menu_choice == "Home":
    st.write("Welcome to the Stock Details App!")

elif menu_choice == "Add New Data":
    st.header("Add New Data")
    Depot = st.text_input("Depot:")
    Location = st.text_input("Location:")
    Item = st.text_input("Item:")
    Make = st.text_input("Make:")
    Configuration = st.text_input("Configuration:")
    Serial_number = st.text_input("Serial_number:")
    Remarks = st.text_input("Remarks:")
    if st.button("Add Data"):
        insert(Depot, Location, Item, Make, Configuration, Serial_number, Remarks)

elif menu_choice == "Update Existing Data":
    st.header("Update Existing Data")
    Id = st.text_input("Enter ID to update:")
    if st.button("Search"):
        update(Id)

elif menu_choice == "Delete Data":
    st.header("Delete Data")
    Id = st.text_input("Enter ID to delete:")
    if st.button("Search"):
        delete(Id)

elif menu_choice == "Search Data":
    st.header("Search Data")
    term = st.text_input("Enter Search Term:")
    sort_by_location = st.checkbox("Sort by Location")
    if st.button("Search"):
        table_data, headers, file_name_prefix, search_term = search(term, sort_by_location)
        if table_data:
            st.write(table_data)
            st.markdown(f"Export Search Results as CSV: [Download](data/{file_name_prefix}.csv)")
        else:
            st.warning("No data found.")

elif menu_choice == "View Data":
    st.header("View Data")
    table_data, headers = view_data()
    if table_data:
        st.write(table_data)
    else:
        st.warning("No data found.")

elif menu_choice == "Export Search Results as Text":
    term = st.text_input("Enter Search Term:")
    if st.button("Export as Text"):
        table_data, headers, _, _ = search(term)
        if table_data:
            text_output = "\n".join(["\t | ".join(map(str, row)) for row in table_data])
            st.text(text_output)
        else:
            st.warning("No data found.")

con.close()
