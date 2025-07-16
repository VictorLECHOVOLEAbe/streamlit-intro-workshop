# running the app with the command
# streamlit run streamlit_app.py

import streamlit as st              # For building the web app
import pandas as pd                 # For data manipulation
# import os                           # For file operations

# import matplotlib.pyplot as plt     # For plotting
# import seaborn as sns               # For advanced plotting    
import snowflake.connector          # For connecting to Snowflake


# Page configuration
st.set_page_config(
    page_title="Survey: Experienta ta cu Python si SQL",
    page_icon="🎓"
    # layout="wide"   
)

# # Global variables
# CSV_FILE = r"survey_responses.csv"


def about():
    # st.title("Despre acest workshop")
    st.header("# Introducere in Streamlit - Workshop 🎓")
    st.markdown("Completati va rog acest formular pentru a ma ajuta sa inteleg nivelul dvs. de experienta si disponibilitatea pentru workshop-ul introductiv in Streamlit.")

    st.header("# Despre acest workshop")
    st.markdown("""
    Acest workshop este destinat celor care doresc sa invete cum sa foloseasca Streamlit pentru a crea aplicatii web interactive cu Python.
    
    **Ce veti invata:**
    - Cum sa instalati si sa configurati Streamlit
    - Cum sa creati interfete de utilizator simple
    - Cum sa adaugati functionalitati interactive
    - Cum sa vizualizati date folosind grafice si tabele
    
    **Cine ar trebui sa participe:**
    - Oricine doreste sa invete Streamlit,
    - Un minim de cunostinte de baza in Python, n-ar strica,
    - Persoane interesate de dezvoltarea de aplicatii web rapide, folosind functionalitati built-in,
    - Cei care doresc sa isi imbunatateasca abilitatile de vizualizare a datelor
    - Data analytics, machine learning, data science, etc.
    """)

    st.markdown((
    "[Streamlit](https://streamlit.io) este o librarie Python care permite crearea de aplicatii interactive, data-driven in Python."
))

def citire_afisare_markdown(file_path):
    """
    Citeste si afiseaza continutul unui fisier markdown.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            st.markdown(content, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Fisierul {file_path} nu a fost gasit.")
    except Exception as e:
        st.error(f"Eroare la citirea fisierului: {e}")


def verificare_nume(nume):
    """
    Verifica daca numele contine doar litere si spatii.
    Verifica daca numele este valid pentru a fi folosit in aplicatie.
    """
    if not nume:
        st.warning("Introduceti numele dvs. pentru a continua.")
        return False

    if len(nume) < 3:
        st.error("Numele trebuie sa aiba cel putin 3 caractere.")
        return False
    if len(nume) > 50:
        st.error("Numele nu poate depasi 50 de caractere.")
        return False
    if not nume.replace(" ", "").isalpha():
        st.error("Numele trebuie sa contina doar litere si spatii.")
        return False
    return True




# Conectare la Snowflake
def conectare_snowflake():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )


# Salvare raspunsuri în Snowflake
def salveaza_in_snowflake(df):
    conn = conectare_snowflake()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO survey_responses (nume, ore_python, librarii, tipuri_fisiere, ore_sql, interval_workshop)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, tuple(row))
    cursor.close()
    conn.close()


# Verifica daca tabelul exista și îl creeaza daca nu exista
def verifica_si_creeaza_tabel():
    conn = conectare_snowflake()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_responses (
                nume STRING,
                ore_developer INT,
                ore_python INT,
                librarii STRING,
                tipuri_fisiere STRING,
                ore_sql INT,
                interval_workshop STRING
            )
        """)
    finally:
        cursor.close()
        conn.close()


# Salveaza datele și afișeaza statusul
def salveaza_in_snowflake(response_df):
    try:
        verifica_si_creeaza_tabel()
        conn = conectare_snowflake()
        cursor = conn.cursor()
        for _, row in response_df.iterrows():
            cursor.execute("""
                INSERT INTO survey_responses (nume, ore_developer, ore_python, librarii, tipuri_fisiere, ore_sql, interval_workshop)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        cursor.close()
        conn.close()
        st.success("✅ Raspunsul tau a fost salvat cu succes în Snowflake. Multumim!")
    except Exception as e:
        st.error(f"Eroare la salvarea în Snowflake: {e}")



def afiseaza_grafic_workshop_din_snowflake():
    try:
        # Conectare la Snowflake
        conn = conectare_snowflake()
        # conn = snowflake.connector.connect(
        #     user=st.secrets["snowflake"]["user"],
        #     password=st.secrets["snowflake"]["password"],
        #     account=st.secrets["snowflake"]["account"],
        #     warehouse=st.secrets["snowflake"]["warehouse"],
        #     database=st.secrets["snowflake"]["database"],
        #     schema=st.secrets["snowflake"]["schema"]
        # )
        

        # Citim toate datele din tabel
        df = pd.read_sql("SELECT interval_workshop FROM survey_responses", conn)
        conn.close()

        # Numaram frecventa fiecarei optiuni
        vote_counts = df["INTERVAL_WORKSHOP"].value_counts().reset_index()
        vote_counts.columns = ["Interval", "Numar de voturi"]
        vote_counts.set_index("Interval", inplace=True)

        # Afișam graficul bar chart orizontal
        st.header("📊 Distributia voturilor pentru intervalul workshop-ului")
        # https://docs.streamlit.io/develop/api-reference/charts/st.bar_chart
        
        st.bar_chart(vote_counts, color=["#ffaa00","#ffaa0088"], horizontal=True)
        
    except Exception as e:
        st.error(f"Eroare la extragerea datelor din Snowflake: {e}")




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
#     salveaza_in_snowflake(response)

#     st.success("✅ Raspunsul tau a fost salvat cu succes. Multumim!")
#     afiseaza_grafic_voturi_din_csv()


def survey_form():
    # Colectare date
    st.header("# Sa ne cunoastem mai bine")

    name = st.text_input("Numele complet:", 
                        placeholder="Introduceti numele dvs. aici", 
                        help="Acest camp este obligatoriu!"
                    )
    # verificare nume
    if not verificare_nume(name):
        st.stop()

    developer_hours = st.number_input("Cum ai descrie experienta ta ca developer exprimata in ore de active coding time?", min_value=0, step=1)

    python_hours = st.number_input("Cum ai descrie experienta ta ca Python developer exprimata in ore de active coding time?", min_value=0, step=1)

    libraries = st.multiselect(
        "Cu ce librarii/framework-uri Python ai lucrat?",
        ["NumPy", "Pandas", "Matplotlib", "Seaborn", "Flask", "Django", "Streamlit", "Alta librarie", "Niciuna"]
    )

    file_types = st.multiselect(
        "Cu ce tipuri de fisiere ai lucrat si esti familiar?",
        [".csv", ".json", ".xlsx", ".sql", ".txt", ".xml", "Alt tip"]
    )

    sql_hours = st.number_input("Cum ai descrie experienta ta ca SQL developer exprimata in ore de active coding time?", min_value=0, step=1)




    workshop_time = st.radio(
        "Care dintre urmatoarele intervale ti s-ar potrivi pentru un workshop introductiv in Streamlit?",
        ("Vineri 09:00-12:00", "Vineri 13:00-16:00")
    )

        # Buton de trimitere
    if st.button("Trimite raspunsul"):
        # Structuram datele intr-un DataFrame
        response = pd.DataFrame([{
            "Nume": name,
            "Ore Developer": developer_hours,
            "Ore Python": python_hours,
            "Librarii": ", ".join(libraries),
            "Tipuri fisiere": ", ".join(file_types),
            "Ore SQL": sql_hours,
            "Interval workshop": workshop_time
        }])


        # salveaza_in_snowflake_check(response)
        salveaza_in_snowflake(response)
        # # Numele fisierului CSV
        # csv_file = r"quizz-app\survey_responses.csv"

        # # Verificam daca fisierul exista deja
        # if os.path.exists(csv_file):
        #     existing = pd.read_csv(csv_file)
        #     updated = pd.concat([existing, response], ignore_index=True)
        #     updated.to_csv(csv_file, index=False)
        # else:
        #     response.to_csv(csv_file, index=False)

        # st.success("✅ Raspunsul tau a fost salvat cu succes. Multumim!")

        # afiseaza_grafic_voturi_din_csv()
        afiseaza_grafic_workshop_din_snowflake()

def afiseaza_grafic_voturi_din_csv():
    # import matplotlib.pyplot as plt
    # import seaborn as sns

    st.subheader("📊 Rezultatele voturilor pentru intervalul workshop-ului")

    # Verificam daca fisierul CSV exista
    if not os.path.exists(CSV_FILE):
        st.warning("Nu exista date disponibile. Trimite cel putin un raspuns pentru a vedea rezultatele.")
        return
    
    # Citim datele din fisierul CSV
    # import pandas as pd
    # import matplotlib.pyplot as plt
    try:

        
        df = pd.read_csv(CSV_FILE)
        vote_counts = df["Interval workshop"].value_counts()

        # Generez automat o lista de culori pentru bar chart
        colors = sns.color_palette("husl", n_colors=len(vote_counts))  # Folosim o paleta de culori din Seaborn


        # # https://matplotlib.org/stable/tutorials/colors/colormaps.html
        # colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']  # albastru, portocaliu, verde, rosu, mov, maro
        fig, ax = plt.subplots(figsize=(10, 1 * len(vote_counts)))  # Ajustam inaltimea in functie de numarul de voturi
        
        # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html

        bars = ax.barh(vote_counts.index, vote_counts.values, color=colors[:len(vote_counts)])
        ax.set_xlabel("Numar de voturi")
        ax.set_title("Distributia voturilor pentru intervalul workshop-ului", fontsize=14, fontweight='bold', loc='center')

        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{int(width)}', va='center')

        st.pyplot(fig)


    except FileNotFoundError:
        st.warning("Fisierul cu raspunsuri nu a fost gasit. Trimite cel putin un raspuns pentru a vedea rezultatele.")



    st.markdown("---")










def main():
    about()
    citire_afisare_markdown("workshop_requirements.md")
    survey_form()

if __name__ == "__main__":
    main()
