import csv
import io
import streamlit as st
#import pandas as pd
from openpyxl import load_workbook
st.set_page_config(page_title="Customer Data Parser")


st.markdown("""
<style>
.stApp {
    background-color: #F3F0FF;
    color: #252044;
}
h1, h2, h3 {
    color: #6941C6 !important;
}
.stButton > button {
    background-color: #6941C6;
    color: white;
    border-radius: 12px;
    border: none;
}
.stButton > button:hover {
    background-color: #5030A0;
    color: white;
}
div[data-testid="stFileUploader"] {
    border: 2px solid #B9A6F4;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("💜 Customer Data Parser")
st.caption("Smart Email Parsing & Customer Data Management")
st.divider()


st.write("Enter your email address below")

email = st.text_input("Enter Email")

if st.button("Parse Email"):

    if "@" in email:

        username = email.split("@")[0]
        domain = email.split("@")[1]
        website = domain.split(".")[0]
        tld = domain.split(".")[-1]

        st.success("Email Parsed Successfully!")

        st.write("Username:", username)
        st.write("Domain:", domain)
        st.write("Top Level Domain:", tld)

    else:
        st.error("Please enter a valid email")
        st.subheader("Upload Customer File")

file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if file is not None:
    if file.name.endswith(".xlsx"):
        workbook = load_workbook(file, read_only=True, data_only=True)
        sheet = workbook.active
        data = list(sheet.values)
        workbook.close()

        st.success("File Uploaded Successfully!")

        if data:
            st.write("Customer Data:")
            st.write("Name | Email")
            st.write("--------------------")

            for row in data[1:]:
                 st.write(row[0], "|", row[1])
            st.write("Total Customers:", len(data) - 1)
            st.subheader("Parsed Customer Emails")

            for row in data[1:]:
                if len(row) >= 2 and row[1]:
                    email = str(row[1]).strip()

                    if "@" in email:
                        username, domain = email.split("@", 1)
                        tld = domain.split(".")[-1]

                        st.write("Email:", email)
                        st.write("Username:", username)
                        st.write("Domain:", domain)
                        st.write("Top Level Domain:", tld)
                        st.write("--------------------")
        else:
            st.warning("Excel file is empty.")
    else:
        st.warning("Please upload an Excel (.xlsx) file.")
        
st.subheader("Search Customer")

search = st.text_input("Enter Customer Name")

    

if search:
    new_results = [
        customer for customer in st.session_state.get("new_customers", [])
        if search.lower() in customer["Name"].lower()
    ]
    if new_results:
        st.write("New Customer Search Results:")
        for customer in new_results:
            st.write("Name:", customer["Name"])
            st.write("Email:", customer["Email"])

    if file is not None and data:
        results = [
            row for row in data[1:]
            if row[0] is not None
            and search.lower() in str(row[0]).lower()
        ]

 
        if results:
          st.write("Search Results:")
          for row in results:
                    st.write("Name:", row[0])
                    st.write("Email:", row[1])
        else:
                st.warning("Customer not found")
    else:
        
        if not new_results:
            st.warning("Please upload a customer file first")

            
#import pandas as pd
st.subheader("📥 Download Cleaned Data")

if file is not None:
    try:
        file.seek(0)

        if file.name.lower().endswith(".csv"):
            text = io.TextIOWrapper(file, encoding="utf-8-sig")
            rows = list(csv.reader(text))
            text.detach()
        else:
            workbook = load_workbook(file, read_only=True, data_only=True)
            rows = list(workbook.active.values)
            workbook.close()

        if rows:
            cleaned_rows = []
            seen = set()

            for row in rows:
                cleaned = tuple(
                    str(value).strip() if value is not None else ""
                    for value in row
                )

                if cleaned not in seen:
                    cleaned_rows.append(cleaned)
                    seen.add(cleaned)

        output = io.StringIO()
        # Add Username, Domain and TLD columns
        new_rows = [list(cleaned_rows[0]) + ["Username", "Domain", "TLD"]]

        for row in cleaned_rows[1:]:
            row = list(row)
            email = str(row[1]).strip()

            username = ""
            domain = ""
            tld = ""

            if email.count("@") == 1:
               username, domain = email.split("@")
               if "." in domain:
                   tld = domain.rsplit(".", 1)[-1]

            new_rows.append(row + [username, domain, tld])

        cleaned_rows = new_rows
        writer = csv.writer(output)
        writer.writerows(cleaned_rows)

        st.success("Data cleaned successfully!")

        st.download_button(
                label="📥 Download Cleaned Data",
                 data=output.getvalue().encode("utf-8-sig"),
                file_name="cleaned_customer_data.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"File processing error: {e}")
    
# Add New Customer
st.header("➕ Add New Customer")

new_name = st.text_input("Enter New Customer Name")
new_email = st.text_input("Enter New Customer Email")

if st.button("Add Customer"):
    if new_name.strip() and "@" in new_email and "." in new_email.split("@")[-1]:
        st.session_state.setdefault("new_customers", [])
       
        email = new_email.strip().lower()

        already_exists = any(
            c["Email"].lower() == email
            for c in st.session_state.new_customers
        )

        if already_exists:
            st.warning("Customer already exists!")
        else:
            st.session_state.new_customers.append({
                "Name": new_name.strip(),
                "Email": new_email.strip()
            })
            st.success("Customer added successfully!")

    else:
        st.error("Please enter a valid name and email.")
