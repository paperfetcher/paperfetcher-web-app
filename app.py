# @author Akash Pallath\

import datetime

import pandas as pd
import streamlit as st

import time

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

st.markdown("---")

# Section 2

st.header("2. What type of search do you want to perform?")

search = st.radio("Select one:", ('Handsearch', 'Snowball-search'))

with st.expander("What's this?"):
    st.markdown("""
                - **Handsearch**:
                - **Snowball-search**:
                """)

st.markdown("---")

# Section 3

# Crossref handsearch
if db == "Crossref" and search == "Handsearch":
    st.header("3. Define your handsearch parameters.")

    # Journals
    st.subheader("a) Select journals to search in.")
    st.write("You can add multiple journals to a single handsearch.")

    col1, col2 = st.columns(2)

    with col1:
        journal_list = load_crossref_journals_dict()
        option = st.selectbox("Search for a journal.",
                              journal_list,
                              index=50000,
                              help="""Type the name of a journal to search for it in the database.
                                    This might be slow due to a large number of entries.
                                    Once you find the journal, click on the 'Add to Search' button.""")

        if st.button("Add to search", key="cr_hs_journal"):
            if 'selected_journals_list' not in st.session_state:
                st.session_state.selected_journals_list = [option]
            else:
                st.session_state.selected_journals_list.append(option)

    with col2:
        issn = st.text_input("Enter an ISSN",
                             help="""If you the know the ISSN of a journal you wish to search within,
                                     you can type it here and click on the 'Add to Search' button.
                                     If the journal has a print ISSN and an electronic ISSN, use the electronic ISSN.""")

        if st.button("Add to search", key="cr_hs_issn"):
            if 'selected_journals_list' not in st.session_state:
                st.session_state.selected_journals_list = [issn]
            else:
                st.session_state.selected_journals_list.append(issn)

    issn_list = st.multiselect("Selected journals to search in",
                               options=st.session_state.selected_journals_list,
                               default=st.session_state.selected_journals_list)

    # Start and end date
    st.subheader("b) Select a date range to fetch articles within.")

    col1, col2 = st.columns(2)

    with col1:
        start = st.date_input("Fetch from this date onwards.",
                              min_value=datetime.date(1900, 1, 1),
                              max_value=datetime.date.today())

    with col2:
        end = st.date_input("Fetch until this date.",
                            min_value=datetime.date(1900, 1, 1),
                            max_value=datetime.date.today())

    # Start and end date
    st.subheader("c) Enter search keywords (optional).")

    keywords = st.text_area(label="Enter comma-separated keywords")

    # Search button
    st.subheader("d) Perform search")
    if st.button("Search"):
        my_bar = st.progress(0)

        for percent_complete in range(100):
            time.sleep(0.1)
            my_bar.progress(percent_complete + 1)

        st.markdown("---")

        # View and save results
        st.header("4. View and save search results")


# Crossref snowballsearch
if db == "Crossref" and search == "Snowball-search":
    st.header("3. Define your snowball-search parameters.")

# PubMed handsearch
if db == "PubMed" and search == "Handsearch":
    st.header("3. Define your handsearch parameters.")

# PubMed snowballsearch
if db == "PubMed" and search == "Snowball-search":
    st.header("3. Define your snowball-search parameters.")
