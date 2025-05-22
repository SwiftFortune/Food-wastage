import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

import mysql.connector
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sh!ne$777Luck",
    database = "food_data",
)
cursor = conn.cursor()
cursor.execute('use food_data')


# Create the sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Project Introduction", "View Tables", "CRUD Operations", "SQL Queries","Learner Queries","User Introduction"])

# Main content based on selection
if page == "Project Introduction": 
    #insert the image
    image_path = r"c:\Users\Sachin Hembram\Downloads\free-food-distribution-social-activity-helping-homeless-people-giving-them-139435924.webp" 
    st.image(image_path)
    # Title
    st.title("🍽 Tacklinsg Food Wastage for a Better Future")

    # Introduction
    st.write("""
    Food is one of the most fundamental human needs, yet millions of people suffer from hunger while vast amounts of edible food go to waste every day. 
    Whether in households, restaurants, or supermarkets, food waste has become a global challenge, contributing to environmental concerns, 
    resource depletion, and economic loss.
    """)

    st.write("""
    To address this issue, our project focuses on developing a **Local Food Wastage Management System**, an innovative platform that connects 
    surplus food providers with individuals and organizations in need. By leveraging technology, we aim to create an efficient, structured system where:
    """)

    # Bullet Points for Features
    st.markdown("""
    - 🍽 **Restaurants and individuals** can list surplus food available for redistribution.
    - 🤝 **NGOs and food-insecure individuals** can easily claim and access the food.
    - 🗄 **SQL databases** store real-time food availability, locations, and other essential details.
    - 🖥 **A Streamlit-based web application** allows seamless interaction, filtering, CRUD operations, and insightful data visualization.
    """)

    # Business Impact & Use Cases
    st.subheader("📈 Business Impact & Use Cases")
    st.write("""
    This initiative is not just about reducing food waste—it's about **making a difference**. The system enables:
    """)

    st.markdown("""
    - 🔗 **Connecting food providers to those in need** through a structured and accessible platform.
    - ♻️ **Efficient redistribution** of surplus food, preventing unnecessary disposal.
    - 📍 **Geolocation features** to help users find food sources nearby, enhancing accessibility.
    - 📊 **Data analytics** to track wastage trends, facilitating informed decision-making for better sustainability.
    """)

    # Footer message
    st.write("By transforming excess food into an opportunity for social good, we contribute to a **more sustainable**, **equitable**, and **compassionate** world—one meal at a time. 💚")



if page == "View Tables":
    st.title("View Tables")

    # Get all table names from the database
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    # Select a table from the dropdown
    select_table = st.selectbox("Select a table", table_names)

    # Input boxes for search
    search_term = st.text_input("Search within the table (text or number):")
    search_id = st.text_input("Search by ID (Exact match):")

    # Fetch table data
    query = f"SELECT * FROM {select_table}"
    cursor.execute(query)
    rows = cursor.fetchall()
    column_names = [i[0] for i in cursor.description]
    df = pd.DataFrame(rows, columns=column_names)

    # Display full table before filtering
    st.subheader(f"Full Data of {select_table}")
    st.dataframe(df)

    # **Text-based search for entire row**
    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        filtered_df = df[mask]

        if not filtered_df.empty:
            st.subheader(f"Filtered Results for '{search_term}'")
            st.dataframe(filtered_df)
        else:
            st.write(f"No records found for '{search_term}'.")

    # **Search by ID separately**
    if search_id:
        try:
            search_id_numeric = int(search_id)
            id_filtered_df = df[df.iloc[:, 0] == search_id_numeric]  # Assuming the first column is the ID column
        except ValueError:
            id_filtered_df = pd.DataFrame()  # Empty result for non-numeric ID input

        if not id_filtered_df.empty:
            st.subheader(f"Details for ID {search_id}")
            st.dataframe(id_filtered_df)
        else:
            st.write(f"No records found for ID {search_id}.")




if page == "CRUD Operations":
    st.title("CRUD Operations")

    # Get all table names from the database
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]

    # Select a table from the dropdown
    select_table = st.selectbox("Select a table", table_names)

    # Fetch and display the selected table data
    query = f"SELECT * FROM {select_table}"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Get column names
    column_names = [i[0] for i in cursor.description]
    df = pd.DataFrame(rows, columns=column_names)

    # Display full table
    st.subheader(f"Full Data of {select_table}")
    st.dataframe(df)

    # Select operation type
    crud_action = st.selectbox("Select an action", ["Add New Entry", "Update Entry", "Delete Entry"])

    # Fetch table structure to dynamically get columns
    cursor.execute(f"DESCRIBE {select_table}")
    columns = [col[0] for col in cursor.fetchall()]

    if crud_action == "Add New Entry":
        st.subheader(f"Add New Entry in {select_table}")

        # Create a form for data entry
        with st.form(key="insert_form"):
            user_inputs = {col: st.text_input(f"Enter {col}") for col in columns}
            submit_button = st.form_submit_button(label="Submit")

            if submit_button:
                placeholders = ", ".join(["%s"] * len(user_inputs))
                cursor.execute(f"""
                    INSERT INTO {select_table} ({", ".join(columns)}) 
                    VALUES ({placeholders})
                """, tuple(user_inputs.values()))
                conn.commit()
                st.success(f"New entry added to {select_table} ✅")
                st.image("success_image.jpg", caption="Submission Successful!")

    elif crud_action == "Update Entry":
        st.subheader(f"Update Entry in {select_table}")

        primary_key = columns[0]  # Assume the first column is the primary key
        existing_ids = df[primary_key].tolist()

        # Select entry to update
        selected_id = st.selectbox(f"Select {primary_key} to update", existing_ids)

        with st.form(key="update_form"):
            update_inputs = {col: st.text_input(f"Update {col}", value=df[df[primary_key] == selected_id][col].values[0]) for col in columns[1:]}
            update_button = st.form_submit_button(label="Update")

            if update_button:
                set_clause = ", ".join([f"{col}=%s" for col in update_inputs.keys()])
                values = list(update_inputs.values()) + [selected_id]

                cursor.execute(f"""
                    UPDATE {select_table} SET {set_clause} WHERE {primary_key}=%s
                """, tuple(values))
                conn.commit()
                st.success(f"Entry updated in {select_table} ✅")
                st.image("update_success.jpg", caption="Update Successful!")

    elif crud_action == "Delete Entry":
        st.subheader(f"Delete Entry in {select_table}")

        primary_key = columns[0]  # Assume the first column is the primary key
        existing_ids = df[primary_key].tolist()

        # Select entry to delete
        selected_id_to_delete = st.selectbox(f"Select {primary_key} to delete", existing_ids)
        delete_button = st.button("Delete")

        if delete_button:
            cursor.execute(f"DELETE FROM {select_table} WHERE {primary_key}=%s", (selected_id_to_delete,))
            conn.commit()
            st.warning(f"Entry deleted from {select_table} ❌")
            st.image("delete_success.jpg", caption="Delete Successful!")





if page == "SQL Queries":
    st.title("SQL Queries")
    Query = { 
        "1. Which type of food provider (restaurant, grocery store, etc.) contributes the most food?":"SELECT type, count(*) AS Type_Count FROM giver GROUP BY type ORDER BY Type_Count ASC",
        "2. What is the contact information of food providers in a specific city?":"SELECT City, Contact FROM giver ORDER BY city ASC;",  
        "3. Count the number of each provider type?":" SELECT Name, Type  FROM giver ORDER BY Name ASC;",
        "4.Retrive providers whose caontact number start with '+1'?":"SELECT Name, Contact FROM giver WHERE Contact LIKE '+1%' ORDER BY Name ASC;",   
        "5. Find all providers located in a city that contains 'port'?":"SELECT Name, City FROM giver WHERE City LIKE 'East%'",
        "6. List all providers sorted Alphabetically by name?":"SELECT Provider_ID, Name, Type, Address, City, Contact FROM giver ORDER BY Name ASC;",
        "7. Which receivers have claimed the most food?":"SELECT Name, COUNT(*) AS Higest_claimed FROM target GROUP BY Name ORDER BY Higest_claimed DESC;",
        "8. Find all NGO?":" SELECT Name, Type FROM target WHERE Type LIKE 'NGO%' ORDER BY Name ASC;",
        "9. Count Total Individuals?":"SELECT COUNT(*) AS Total_Individual FROM target WHERE Type = 'Individual'",
        "10. Sort Receivers by city Alphabetically?":"SELECT Receiver_ID, Name, Type, City, Contact FROM target ORDER BY City ASC;",
        "11. Find the 5 Cities with the most receivers?":"SELECT City, COUNT(*) AS Higest_receivers FROM target GROUP BY City ORDER BY Higest_receivers DESC LIMIT 5", 
        "12. What is the total quantity of food available from all providers?":"SELECT Provider_Type, COUNT(*) AS Provider_count, sum(Quantity) AS Total_Quantity  FROM provisions GROUP BY Provider_Type",
        "13. Which city has the highest number of food listing?":"SELECT Location, COUNT(*) AS Number_of_Listings FROM provisions GROUP BY Location ORDER BY Number_of_Listings DESC LIMIT 1;",
        "14. What are the most connonly available food types?":"SELECT Food_Type, COUNT(*) AS Available FROM provisions GROUP BY Food_Type ORDER BY Available DESC;",
        "15. What are the most commonly Meal type?":"SELECT Meal_Type, COUNT(*) AS Available FROM provisions GROUP BY Meal_Type ORDER BY Available DESC LIMIT 5",
        }
    selected_query = st.selectbox("Choose a Query", list(Query.keys()))
    cursor.execute(Query[selected_query])  # Execute the selected query
    query_data = cursor.fetchall()  # Fetch all results

    # Get column names dynamically
    column_names = [desc[0] for desc in cursor.description]

    # Convert result into a DataFrame
    query_result = pd.DataFrame(query_data, columns=column_names)

    st.write("### Query Result:")
    st.dataframe(query_result)


   
if page == "Learner Queries":
    st.title("Learner Queries")
    Query1 = {
        "16. Retrive all avaiable provider_type":"SELECT Provider_Type, COUNT(*) AS Available FROM provisions GROUP BY Provider_Type ORDER BY Available DESC",
        "17.Find all vegan means":"SELECT Meal_Type, Food_Type, COUNT(*) AS list  FROM provisions  WHERE Food_Type = 'Vegan'  GROUP BY Meal_Type, Food_Type;",
        "18. How many food claims have been made for each food item?":"SELECT Status, COUNT(*) AS Delivered FROM petitions WHERE Status = 'Completed'  GROUP BY Status ORDER BY Delivered ASC;",    
        "19. What percentage of food claims are completed vs. pending vs. canceled?":"SELECT Status, COUNT(*) AS Total_Claims, ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM petitions)), 2) AS Percentage FROM petitions GROUP BY Status;",
        "20. How many are there in pending?":"SELECT Status, COUNT(*) AS Received FROM petitions WHERE Status = 'Pending' GROUP BY Status ORDER BY Received DESC",
        "21.Find Food Claims with Full Details":"SELECT a.Claim_ID, a.Food_ID, a.Receiver_ID, a.Status, a.Timestamp, b.Food_Name, b.Quantity, b.Expiry_Date, b.Provider_Type, b.Location, b.Food_type, b.Meal_Type FROM petitions AS a INNER JOIN provisions AS b ON a.Food_ID = b.Food_ID",
        "22. Find expiring food Items that have not been claimed yet?":"SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, f.Location  FROM provisions AS f LEFT JOIN petitions AS c ON f.Food_ID = c.Food_ID WHERE c.Food_ID IS NULL AND f.Expiry_Date <= CURDATE() ORDER BY f.Expiry_Date ASC;",
        "23.List unclaimed food listing by Restaurant":"SELECT a.Food_ID, a.Status, b.Provider_Type, b.Meal_Type FROM petitions AS a LEFT JOIN provisions AS b ON a.Food_ID = b.Food_Id WHERE b.Provider_Type != 'Restaurant'",
        "24.Which meal type is claimed the most?":"SELECT Food_Type, COUNT(*) FROM petitions JOIN provisions ON petitions.Food_ID = provisions.Food_ID GROUP BY Food_Type ORDER BY COUNT(*) DESC LIMIT 5;",
        "25. What is the average quantity of food claimed per receiver?":"SELECT Receiver_ID, AVG(Quantity) FROM petitions JOIN provisions ON petitions.Food_ID = provisions.Food_ID GROUP BY Receiver_ID ORDER BY AVG(Quantity)",
        "26. What is the total quantity of food donated by each provider?":"SELECT giver.Provider_ID, SUM(Quantity) FROM giver JOIN provisions  ON giver.Provider_Id = provisions.Provider_Id GROUP BY Provider_ID ORDER BY SUM(Quantity) DESC;",
        }

    selected_query = st.selectbox("Choose a Query", list(Query1.keys()))
    cursor.execute(Query1[selected_query])  # Execute the selected query
    query_data = cursor.fetchall()  # Fetch all results

    # Get column names dynamically
    column_names = [desc[0] for desc in cursor.description]

    # Convert result into a DataFrame
    query_result = pd.DataFrame(query_data, columns=column_names)

    st.write("### Query Result:")
    st.dataframe(query_result)

if page == "User Introduction":    

    # Display the image
    image_path = r"C:\Users\Sachin Hembram\Downloads\sachin.png" 
    st.image(image_path)


    # Title and Introduction
    st.title("About Me")
    st.write("""
    ### **Sachin Hembram**  
    I hail from **West Bengal** and completed my higher secondary education at 🏫**Sultanpur Vidhyamandir School**, a Bengali-medium institution. Later, I pursued my graduation at 🎓**Arul Anandar College**, affiliated with **Kamraj University, Madurai**.

    Currently, I work as an 🧾**Accountant** at a school in **Uttar Pradesh**, handling financial records and ensuring smooth operations. My passion for learning has led me to explore the dynamic world of 💻 **Data Science**. 

    Two months ago, I embarked on a journey with **Guvi**, enrolling in their Data Science course. While the subject initially seemed challenging, structured learning and self-study have helped me grow, and I now find the process truly enjoyable.

    I am eager to integrate my analytical skills and financial expertise with data-driven insights to contribute meaningfully in my field.
    """)

    # Footer
    st.markdown("---")
    st.write("🔗 **www.linkedin.com/in/sachin-hembram-aa8225305**")  # 
