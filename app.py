# @author Akash Pallath

import streamlit as st
import pandas as pd

################################################################################
# Supporting functions
################################################################################

CROSSREF_JOURNALS_CSV_URL = "http://ftp.crossref.org/titlelist/titleFile.csv"


@st.cache(persist=True)
def load_crossref_journals_dict():
    data = pd.read_csv(CROSSREF_JOURNALS_CSV_URL)
    return (data[['JournalTitle', 'pissn', 'eissn']])


################################################################################
# App display and control flow
################################################################################

st.title("Paperfetcher")
st.write("Automate handsearch for your systematic review.")

# Section 1

st.header("1. Choose a database to search in.")

db = st.radio("Select one:",
              ('Crossref', 'PubMed'))

with st.expander("Need help?"):
    st.markdown("""
                Paperfetcher works by searching for citations in supported databases.
                You can choose from the following databases:
                - **Crossref**: Crossref contains metadata for over 100 million records from journals, books,
                  conference proceedings, etc. across a variety of disciplines.
                  To learn more about Crossref, visit [Crossref.org](https://www.crossref.org).
                - **PubMed**: PubMed contains metadata of over 30 million records from biomedical literature.
                  To learn more about PubMed, visit [PubMed.gov](https://pubmed.ncbi.nlm.nih.gov)
                """)

# Section 2

st.header("2. What type of search do you want to perform?")

search = st.radio("Select one:", ('Handsearch', 'Snowball-search'))

with st.expander("What's this?"):
    st.markdown("""
                - **Handsearch**:
                - **Snowball-search**:
                """)

# Section 3

# Crossref handsearch
if db == "Crossref" and search == "Handsearch":
    st.header("3. Define your handsearch parameters.")

    # Journal ISSN
    journal_list = load_crossref_journals_dict()
    option = st.selectbox("Search for a journal.", journal_list, index=50000)

# Crossref snowballsearch
if db == "Crossref" and search == "Snowball-search":
    st.header("3. Define your snowball-search parameters.")

# Pubmed handsearch
if db == "PubMed" and search == "Handsearch":
    st.header("3. Define your handsearch parameters.")

# Pubmed snowballsearch
if db == "PubMed" and search == "Snowball-search":
    st.header("3. Define your snowball-search parameters.")
