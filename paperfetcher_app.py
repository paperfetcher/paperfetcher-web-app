# @author Akash Pallath
# This code is licensed under the MIT license (see LICENSE.txt for details).

import datetime
import logging
import os

import pandas as pd
import streamlit as st

from paperfetcher import GlobalConfig
from paperfetcher import handsearch, snowballsearch
from paperfetcher.exceptions import SearchError

################################################################################
# Init config
################################################################################

__version__ = 1.0

################################################################################
# Init config
################################################################################

st.set_page_config(layout="wide")

# Allow progress bars
GlobalConfig.streamlit = True

# Set paperfetcher loglevel if paperfetcher_loglevel environment variable is defined,
# else default to INFO
st_loglevel = logging.getLevelName(os.environ.get("paperfetcher_loglevel", "INFO"))
GlobalConfig.loglevel = st_loglevel
print("Streamlit loglevel {}".format(st_loglevel))

# Set limit on size of search
# This is to prevent cloud instances from exceeding resource limits
result_limit = int(os.environ.get("paperfetcher_searchlimit", None))

################################################################################
# Constants
################################################################################

# URL for the CSV file of all journals indexed in crossref
CROSSREF_JOURNALS_CSV_URL = "http://ftp.crossref.org/titlelist/titleFile.csv"

################################################################################
# Supporting functions
#
# All functions that perform data-processing go here.
################################################################################


# Cache to avoid repeated loading and processing of >10 MB data.
@st.cache(persist=True)
def load_crossref_journals_dict():
    data = pd.read_csv(CROSSREF_JOURNALS_CSV_URL)
    issn_title_df = data[['eissn', 'JournalTitle']]
    return issn_title_df.dropna()


if 'search_complete' not in st.session_state:
    st.session_state.search_complete = False

if 'report' not in st.session_state:
    st.session_state.report = ""

if 'results' not in st.session_state:
    st.session_state.results = None


################################################################################
# App display and control flow.
################################################################################

st.title("Paperfetcher")
st.write("Automate handsearch for your systematic review.")

with st.expander("If you use this tool in your research, please cite Pallath and Zhang (2021). Paperfetcher: A tool to automate handsearch for systematic reviews. arXiv:2110.12490 [cs.IR]. (click to expand BibTeX)"):
    st.code("""
@misc{pallath2021paperfetcher,
      title={Paperfetcher: A tool to automate handsearch for systematic reviews},
      author={Akash Pallath and Qiyang Zhang},
      year={2021},
      eprint={2110.12490},
      archivePrefix={arXiv},
      primaryClass={cs.IR}
}
""", language="latex")

################################################################################
# Section 2
# Choose a search type (handsearch or snowball search)
################################################################################

st.header("What type of search do you want to perform?")

search = st.radio("Select one:", ('Handsearch',
                                  'Snowball-search'))

st.markdown("---")

################################################################################
# Section 3
# Search-specific information collection + execution
#
# - Collect all the user-specified parameters required to perform a search
# with paperfetcher.
# - Perform a dry run to check size of search results
# - Check that the search is feasible, i.e., it does not use up too many resources
# - Perform search!
# - Display celebratory snowflakes!
################################################################################

if search == "Handsearch":
    st.header("Define your handsearch parameters.")

    # Journals
    st.subheader("a) Select journals to search in.")
    st.write("""You can add multiple journals to a single handsearch.
                You can either search for a journal by its name using the select box on the left,
                or enter its ISSN in the text box on the right. To add a journal to the handsearch, click on
                the 'Add to search' button below your entry.""")

    col1, col2 = st.columns(2)

    with col1:
        # df with eissn and journal title as columns
        journal_df = load_crossref_journals_dict()
        merged = journal_df['JournalTitle'].astype(str) + ", ISSN:" + journal_df['eissn']
        journal_list = merged.to_list()
        journal_list.insert(0, "")

        # Display journal titles and eISSNs
        option = st.selectbox("Type to search for a journal.",
                              journal_list,
                              index=0,
                              help="""Search for journals indexed in Crossref.
                                      The drop-down menu will update as you type.
                                      Once you find a journal you want to fetch papers from, click on 'Add to search'.
                                      Warning: this may be slow, as you're searching in a list of {} journals!""".format(len(journal_list)))

        # List of ISSNs is stored as a session variable called
        # cr_hs_selected_journals_list
        # Initialize this variable:
        if 'cr_hs_selected_journals_list' not in st.session_state:
            st.session_state.cr_hs_selected_journals_list = []

        if st.button("Add to search", key="cr_hs_journal"):
            if option.strip() == "":
                st.error('You must select a journal first!')
            else:
                st.session_state.cr_hs_selected_journals_list.append(option)

    with col2:
        issn = st.text_input("Enter an ISSN",
                             help="""If you the know the ISSN of a journal you wish to search within,
                                     you can type it here and click on the 'Add to Search' button.
                                     If the journal has a print ISSN and an electronic ISSN, use the electronic ISSN.""")

        if st.button("Add to search", key="cr_hs_issn"):
            if issn.strip() == "":
                st.error('You must select a journal first!')
            else:
                st.session_state.cr_hs_selected_journals_list.append(issn)

    st.write("The journals you selected appear below. If you wish to remove a journal from the search, click on the 'X' next to it.")

    issn_list = st.multiselect("Selected journals (ISSNs) to search in",
                               help="""This is the final list of journals paperfetcher will fetch data from.
                                       Click on the 'X' next to the journal name to remove it from the search.
                                       You can always add it back later from the drop-down menu.""",
                               options=st.session_state.cr_hs_selected_journals_list,
                               default=st.session_state.cr_hs_selected_journals_list)

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

    # Keywords
    st.subheader("c) Enter search keywords [optional].")

    with st.expander("Click to expand."):
        st.write("You can refine your search using keywords.")
        keywords = st.text_area(label="Enter comma-separated keywords")

    st.subheader("d) Select output format.")

    st.write("""You can choose from two output formats:""")
    st.markdown("""
                - A text file of DOIs (.txt): Each DOI appears on a separate line.
                You can use this data to import papers into citation management programs such as Zotero ([instructions](https://www.zotero.org/support/adding_items_to_zotero#add_item_by_identifier)).
                - An RIS citation file (.ris): Contains metadata and abstracts (if available on Crossref) for each paper.
                You can directly import this file into both citation management programs such as Zotero ([instructions](https://www.zotero.org/support/adding_items_to_zotero#importing_from_other_tools)) and systematic review screening tools such as Covidence ([instructions](https://support.covidence.org/help/study-imports)).""")

    formats = {"doi-txt": 'A text file of DOIs (.txt).',
               "ris": 'RIS with abstracts (.ris)'}

    out_format = st.radio("How would you like to download your results?",
                          list(formats.keys()),
                          format_func=lambda fmt: formats[fmt])

    # Search button
    st.subheader("Perform search")

    if st.button("Search"):
        # Parse selected parameters
        if keywords == "" or keywords is None:
            keywords = None
        else:
            keywords = list(keywords.strip().split(","))

        fromd = start
        untild = end

        results = None

        # Evaluate size of search
        expected_size = 0

        for issn_idx, issn_val in enumerate(issn_list):
            if "," in issn_val:
                issn = issn_val.split(",")[1].strip()
            else:
                issn = issn_val
            with st.spinner("Evaluating size of search (ISSN {})".format(issn_val)):
                try:
                    search = handsearch.CrossrefSearch(ISSN=issn,
                                                       keyword_list=keywords,
                                                       from_date=fromd,
                                                       until_date=untild)
                    expected_size += search.dry_run()
                except SearchError as e:
                    st.error("Evaluation for ISSN {} failed. Error message: ".format(issn) + str(e))

        # Check that search does not exceed resource limits
        if result_limit is not None and expected_size > result_limit:
            st.error("""This search will return {} results.
            Unfortunately, due to resource limitations, the cloud version of Paperfetcher cannot support
            searches that return more than {} results.""".format(expected_size, result_limit))
        else:
            # Perform search
            st.info('This search will return {} results'.format(expected_size))

            my_bar = st.progress(0)

            for issn_idx, issn_val in enumerate(issn_list):
                if "," in issn_val:
                    issn = issn_val.split(",")[1].strip()
                else:
                    issn = issn_val

                with st.spinner('Fetching articles from {}'.format(issn_val)):
                    try:
                        search = handsearch.CrossrefSearch(ISSN=issn,
                                                           keyword_list=keywords,
                                                           from_date=fromd,
                                                           until_date=untild)

                        if out_format == 'doi-txt':
                            # Only fetch DOIs
                            search(select=True, select_fields=["DOI"])

                            if results is None:
                                results = search.get_DOIDataset()
                            else:
                                results.extend_dataset(search.get_DOIDataset())

                        elif out_format == 'ris':
                            # Fetch DOIs and abstracts
                            search(select=True, select_fields=["DOI", "abstract"])

                            if results is None:
                                results = search.get_RISDataset(extra_field_list=["abstract"],
                                                                extra_field_parser_list=[None],
                                                                extra_field_rispy_tags=["notes_abstract"])
                            else:
                                results.extend_dataset(search.get_RISDataset(extra_field_list=["abstract"],
                                                                             extra_field_parser_list=[None],
                                                                             extra_field_rispy_tags=["notes_abstract"]))

                    except SearchError as e:
                        st.error("Search for ISSN {} failed. Error message: ".format(issn) + str(e))

                my_bar.progress((issn_idx + 1.0) / len(issn_list))

            st.session_state.results = results

            st.session_state.search_complete = True

            st.success('Search complete!')

            if keywords is not None:
                keywords = ",".join(keywords)
            else:
                keywords = "None"

            report = """Search performed on {date} using Paperfetcher web-app v{version}.

    Search type: Handsearch

    Journals/ISSNs searched:
    {issns}

    Between: {start} and {end}.

    Keywords: {keywords}

    Fetched article count: {count}""".format(date=datetime.date.today().strftime("%B %d, %Y"),
                                             version=__version__,
                                             issns="\n".join(["- {}".format(issn) for issn in issn_list]),
                                             start=start,
                                             end=end,
                                             keywords=keywords,
                                             count=len(results))

            st.session_state.report = report

elif search == "Snowball-search":
    st.header("Define your snowball-search parameters.")

    # Papers
    st.subheader("a) Select the papers you want to start from.")
    st.write("Enter the DOIs of the papers you want to start from. You can add multiple DOIs to a single snowball-search. Separate DOIs with commas.")

    dois = st.text_area("Enter comma-separated DOIs")

    st.subheader("b) Select type of snowball-search.")

    st.write("""You can either perform backward reference chasing or forward citation chasing:""")
    st.markdown("""
                - Backward reference chasing: For each article X, find all the articles which X cites.
                - Forward citation chasing: For each article X, find all the articles which cite X.""")

    types = {"backward": 'Search references (backward reference chasing).',
             "forward": 'Search citing articles (forward citation chasing)'}

    snowball_type = st.radio("Select an option:",
                             list(types.keys()),
                             format_func=lambda fmt: types[fmt])

    st.subheader("c) Select output format.")

    st.write("""You can choose from two output formats:""")
    st.markdown("""
                - A text file of DOIs (.txt): Each DOI appears on a separate line.
                You can use this data to import papers into citation management programs such as Zotero ([instructions](https://www.zotero.org/support/adding_items_to_zotero#add_item_by_identifier)).
                - An RIS citation file (.ris): Contains metadata for each paper.
                You can directly import this file into both citation management programs such as Zotero ([instructions](https://www.zotero.org/support/adding_items_to_zotero#importing_from_other_tools)) and systematic review screening tools such as Covidence ([instructions](https://support.covidence.org/help/study-imports)).""")

    formats = {"doi-txt": 'A text file of DOIs (.txt).',
               "ris": 'RIS with abstracts (.ris)'}

    out_format = st.radio("How would you like to download your results?",
                          list(formats.keys()),
                          format_func=lambda fmt: formats[fmt])

    # Search button
    st.subheader("Perform search")

    if st.button("Search"):
        results = None

        if "," in dois:
            dois = [doi.strip() for doi in dois.split(",")]
        else:
            dois = [dois]

        print(dois)

        if snowball_type == "backward":
            with st.spinner('Fetching references.'):
                search = snowballsearch.CrossrefBackwardReferenceSearch(dois)
                search()

            if out_format == 'doi-txt':
                results = search.get_DOIDataset()

            elif out_format == "ris":
                results = search.get_RISDataset()

        elif snowball_type == "forward":
            with st.spinner('Fetching citations.'):
                search = snowballsearch.COCIForwardCitationSearch(dois)
                search()

            if out_format == 'doi-txt':
                results = search.get_DOIDataset()

            elif out_format == "ris":
                results = search.get_RISDataset()

        st.session_state.results = results

        st.session_state.search_complete = True

        st.success('Search complete!')

        report = """Search performed on {date} using Paperfetcher web-app v{version}.

Search type: {type}

Search DOIs:
{dois}

Fetched DOI count: {count}""".format(date=datetime.date.today().strftime("%B %d, %Y"),
                                     version=__version__,
                                     type=types[snowball_type],
                                     dois="\n".join(["- {}".format(doi) for doi in dois]),
                                     count=len(results))

        st.session_state.report = report

################################################################################
# Display results
################################################################################

if st.session_state.search_complete:
    st.header("Search report")

    st.write("Click on the icon at the top right of the box to copy this report to clipboard.")

    st.code(st.session_state.report)

    st.header("Results")

    st.write("Download search results to your computer.")

    if st.session_state.results is not None:
        if out_format == 'doi-txt':
            st.download_button(label="Download results (.txt file)",
                               data=st.session_state.results.to_txt_string())

        elif out_format == 'ris':
            st.download_button(label="Download results (.ris file)",
                               data=st.session_state.results.to_ris_string())
