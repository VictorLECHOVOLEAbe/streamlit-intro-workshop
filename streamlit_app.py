
# Run the app with the command:
# streamlit run streamlit_app.py

import streamlit as st              # For building the web app
import pandas as pd                 # For data manipulation
# import os                           # For file operations

# import matplotlib.pyplot as plt     # For plotting
# import seaborn as sns               # For advanced plotting    
import snowflake.connector          # For connecting to Snowflake


# Page configuration
st.set_page_config(
    page_title="Survey: Your Experience with Python and SQL",
    page_icon="🎓"
    # layout="wide"   
)


# # Global variables
# CSV_FILE = r"survey_responses.csv"


def about():
    # st.title("About this workshop")
    st.header("# Introduction to Streamlit - Workshop 🎓")
    st.markdown("Please complete this form to help me understand your experience level and availability for the introductory Streamlit workshop.")

    st.header("# About this workshop")
    st.markdown("""
    This workshop is intended for those who want to learn how to use Streamlit to create interactive web applications with Python.
    
    **What you will learn:**
    - How to install and configure Streamlit
    - How to create simple user interfaces
    - How to add interactive features
    - How to visualize data using charts and tables
    
    **Who should attend:**
    - Anyone who wants to learn Streamlit,
    - A minimum of basic Python knowledge is helpful,
    - People interested in developing fast web applications using built-in features,
    - Those who want to improve their data visualization skills
    - Data analytics, machine learning, data science, etc.
    """)

    st.markdown((
    "[Streamlit](https://streamlit.io) is a Python library that allows you to create interactive, data-driven applications in Python."
))

def read_and_display_markdown(file_path):
    """
    Reads and displays the content of a markdown file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            st.markdown(content, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File {file_path} was not found.")
    except Exception as e:
        st.error(f"Error reading file: {e}")


def validate_name(name):
    """
    Checks if the name contains only letters and spaces.
    Checks if the name is valid to be used in the application.
    """
    if not name:
        st.warning("Please enter your name to continue.")
        return False

    if len(name) < 3:
        st.error("The name must have at least 3 characters.")
        return False
    if len(name) > 50:
        st.error("The name cannot exceed 50 characters.")
        return False
    if not name.replace(" ", "").isalpha():
        st.error("The name must contain only letters and spaces.")
        return False
    return True



# Connexion to Snowflake
# https://docs.snowflake.com/en/user-guide/python-connector.html
# import snowflake.connector
# https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect#connecting-using-the-connections-toml-file
def snowflake_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )


# Salvare raspunsuri în Snowflake
def snowflake_insert_into(df):
    # https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example
    conn = snowflake_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO survey_responses (name, python_hours, libraries, file_types, sql_hours, workshop_proposed_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, tuple(row))
    cursor.close()
    conn.close()


# Checking if the table exists and creating it if it does not
# https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-example#creating-a-table
def create_if_not_exists_table():
    # Using the connection already defined in the snowflake_connection function
    conn = snowflake_connection()
    
    # Approach 1: Using a cursor to execute SQL commands
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_responses (
                name STRING,
                developer_hours INT,
                python_hours INT,
                libraries STRING,
                file_types STRING,
                sql_hours INT,
                workshop_proposed_time STRING
            )
        """)
    finally:
        cursor.close()
        conn.close()

    # # Approach 2: Using a context manager to ensure the connection is closed automatically
    # # We can use also with statement to ensure the connection is closed automatically
    # with snowflake_connection() as conn:
    #     with conn.cursor() as cursor:
    #         cursor.execute("""
    #             CREATE TABLE IF NOT EXISTS survey_responses (
    #                 name STRING,
    #                 developer_hours INT,
    #                 python_hours INT,
    #                 libraries STRING,
    #                 file_types STRING,
    #                 sql_hours INT,
    #                 workshop_proposed_time STRING
    #             )
    #         """)

# Snowflake insert function
# This function inserts the response DataFrame into the Snowflake table
def snowflake_insert_into(response_df):
    try:
        # Ensure the table exists before inserting data
        create_if_not_exists_table()

        # Connect to Snowflake and insert the data
        conn = snowflake_connection()


        # Using approach 1: Using a cursor to execute SQL commands
        cursor = conn.cursor()
        for _, row in response_df.iterrows():
            cursor.execute("""
                INSERT INTO survey_responses (name, developer_hours, python_hours, libraries, file_types, sql_hours, workshop_proposed_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        cursor.close()
        conn.close()
        
        # # Using approach 2: Using a context manager to ensure the connection is closed automatically
        # with snowflake_connection() as conn:
        #     with conn.cursor() as cursor:
        #         for _, row in response_df.iterrows():
        #             cursor.execute("""
        #                 INSERT INTO survey_responses (name, developer_hours, python_hours, libraries, file_types, sql_hours, workshop_proposed_time)
        #                 VALUES (%s, %s, %s, %s, %s, %s, %s)
        #             """, tuple(row))

        st.success("✅ Your response has been successfully saved in Snowflake. Thank you!")
        st.balloons()  # Optional: Show balloons animation on success
    except Exception as e:

        st.error(f"Error saving to Snowflake: {e}")



def display_workshop_proposed_time_from_snowflake():
    try:
        # Define the connection to Snowflake
        # Using the connection already defined in the snowflake_connection function
        conn = snowflake_connection()
        # conn = snowflake.connector.connect(
        #     user=st.secrets["snowflake"]["user"],
        #     password=st.secrets["snowflake"]["password"],
        #     account=st.secrets["snowflake"]["account"],
        #     warehouse=st.secrets["snowflake"]["warehouse"],
        #     database=st.secrets["snowflake"]["database"],
        #     schema=st.secrets["snowflake"]["schema"]
        # )
        

        # # Approach 1: Using a cursor to execute SQL commands
        # cursor = conn.cursor()
        # sql_query = "SELECT workshop_proposed_time FROM survey_responses"
        # cursor.execute(sql_query)
        # # Fetch all results into a DataFrame
        # # Using pandas to read the SQL query results directly into a DataFrame
        # df = cursor.fetch_pandas_all()  # This will return a DataFrame with all results
        # cursor.close()

        # # Approach 2: Using a context manager to ensure the connection is closed automatically
        # with snowflake_connection() as conn:
        #     with conn.cursor() as cursor:
        #         sql_query = "SELECT workshop_proposed_time FROM survey_responses"
        #         cursor.execute(sql_query)
        #         # Fetch all results into a DataFrame
        #         df = cursor.fetch_pandas_all()
        
        # Approach 3: Using pandas to read the SQL query results directly into a DataFrame
        
        df = pd.read_sql("SELECT workshop_proposed_time FROM survey_responses", conn)
        conn.close()

        # # Approach 4: using chunks to read the SQL query results directly into a DataFrame
        # df = pd.read_sql("SELECT workshop_proposed_time FROM survey_responses", conn, chunksize=1000)
        # conn.close()   

        # # # Approach 5: Using fetch_pandas_all() to read the SQL query results directly into a DataFrame
        # # https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-pandas#migrating-to-pandas-dataframes
        # with conn.cursor() as cursor:
        #     sql_query = "SELECT workshop_proposed_time FROM survey_responses"
        #     cursor.execute(sql_query)
        #     # Fetch all results into a DataFrame
        #     df = cursor.fetch_pandas_all()
        #     import pandas as pd

        # def fetch_pandas_old(cursor, sql):
        #     cursor.execute(sql)
        #     rows = 0
        #     while True:
        #         dat = cursor.fetchmany(50000)
        #         if not dat:
        #             break
        #         df = pd.DataFrame(dat, columns=cursor.description)
        #         rows += df.shape[0]
        #     print(rows)

        # # import pandas as pd
        # def fetch_pandas_sqlalchemy(sql):
        #     rows = 0
        #     for chunk in pd.read_sql_query(sql, engine, chunksize=50000):
        #         rows += chunk.shape[0]
        #     print(rows)
            
        # Using fetch_pandas_all() to read the SQL query results directly into a DataFrame
        # # df = pd.read_sql("SELECT workshop_proposed_time FROM survey_responses", conn, chunksize=1000)
        # # conn.close()     



        # Using pandas, counting the number of votes for each proposed workshop time interval
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.value_counts.html
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.set_index.html
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.columns.html
        # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas

        vote_counts = df["WORKSHOP_PROPOSED_TIME"].value_counts().reset_index()
        vote_counts.columns = ["Interval", "Votes Number"]
        vote_counts.set_index("Interval", inplace=True)

        # Display the results in Streamlit using a horizontal bar chart
        st.header("📊Vote distribution for the workshop time interval")
        # https://docs.streamlit.io/develop/api-reference/charts/st.bar_chart
        
        # st.bar_chart(vote_counts, color=["#ffaa00","#0088ffb5"], horizontal=True)
        # st.bar_chart(vote_counts, color=["#A3C4F3", "#90D5EC", "#B5EAD7"], horizontal=True)
        # still issue: Error retrieving data from Snowflake: The list of colors ['#A3C4F3', '#90D5EC', '#B5EAD7'] must have the same length as the list of columns to be colored ['Votes Number'].
        st.bar_chart(vote_counts, 
                     horizontal=True
        )
    
    except Exception as e:
        st.error(f"Error retrieving data from Snowflake: {e}")
        




# def salveaza_si_afiseaza_status(response):
#     """
#     Salveaza raspunsul in fisierul CSV si afiseaza un mesaj de succes.
#     """
#     # Verificam daca fisierul CSV exista deja
#     if os.path.exists(CSV_FILE):
#         existing = pd.read_csv(CSV_FILE)
#         updated = pd.concat([existing, response], ignore_index=True)
#         updated.to_csv(CSV_FILE, index=False)
#     else:
#         response.to_csv(CSV_FILE, index=False)

#     # Salveaza in Snowflake
#     snowflake_insert_into(response)

#     st.success("✅ Raspunsul tau a fost salvat cu succes. Multumim!")
#     display_graph_votes_from_csv()


def survey_form():
    # Data collection
    st.markdown("---")
    st.header("#Let's get to know each other better")

    name = st.text_input("Full name:", 
                        placeholder="Enter your name here", 
                        help="This field is required!"
                    )
    # name validation
    if not validate_name(name):
        st.stop()

    developer_hours = st.number_input("How would you describe your experience as a developer (active coding hours)?", min_value=0, step=1)

    python_hours = st.number_input("How would you describe your experience as a Python developer (active coding hours)?", min_value=0, step=1)

    libraries = st.multiselect(
        "Which Python libraries/frameworks have you worked with?",
        ["NumPy", "Pandas", "Matplotlib", "Seaborn", "Flask", "Django", "Streamlit", "Other library", "None"]
    )

    file_types = st.multiselect(
        "Which file types have you worked with and are familiar with?",
        [".csv", ".json", ".xlsx", ".sql", ".txt", ".xml", "Other type"]
    )

    sql_hours = st.number_input("How would you describe your experience as a SQL developer (active coding hours)?", min_value=0, step=1)

    workshop_proposed_time = st.radio(
        "Which of the following time slots would suit you for an introductory Streamlit workshop?",
        ("Friday 09:00-12:00", "Friday 13:00-16:00", "Not available this Friday anymore")
    )

    # Submit button
    if st.button("Submit response"):
        # Structure the data in a DataFrame
        response = pd.DataFrame([{
            "Full Name": name,
            "Developer Hours": developer_hours,
            "Python Hours": python_hours,
            "Libraries": ", ".join(libraries),
            "File Types": ", ".join(file_types),
            "SQL Hours": sql_hours,
            "Workshop Proposed Time": workshop_proposed_time
        }])


        snowflake_insert_into(response)
        display_workshop_proposed_time_from_snowflake()

def display_graph_votes_from_csv():
    # import matplotlib.pyplot as plt
    # import seaborn as sns

    st.header("📊 Rezultatele voturilor pentru intervalul workshop-ului")

    # checking if the CSV file exists using os.path.exists
    # import os
    if not os.path.exists(CSV_FILE):
        st.warning("Nu exista date disponibile. Trimite cel putin un raspuns pentru a vedea rezultatele.")
        return
    
    # Reading data from the csv using pandas
    # import pandas as pd
    # import matplotlib.pyplot as plt
    try:
        df = pd.read_csv(CSV_FILE)
        vote_counts = df["Interval workshop"].value_counts()

        # Automatic generation of a color pallet to use in the bar chart
        colors = sns.color_palette("husl", n_colors=len(vote_counts))  # using a palet color from Seaborn


        # # https://matplotlib.org/stable/tutorials/colors/colormaps.html
        # colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']  # albastru, portocaliu, verde, rosu, mov, maro
        fig, ax = plt.subplots(figsize=(10, 1 * len(vote_counts)))  # Ajust the height of the figure based on the number of vote counts
        
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html

        bars = ax.barh(vote_counts.index, vote_counts.values, color=colors[:len(vote_counts)])
        ax.set_xlabel("Votes Number")
        ax.set_title("📊Votes distribution", fontsize=14, fontweight='bold', loc='center')

        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center')

        st.pyplot(fig)


    except FileNotFoundError:
        st.warning("The file with responses was not found. Please submit at least one response to see the results.")
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")


    st.markdown("---")










def main():
    # about()
    read_and_display_markdown("about.md")
    read_and_display_markdown("workshop_requirements.md")
    survey_form()

if __name__ == "__main__":
    main()
