# paperfetcher-app

This repository contains the *Paperfetcher* streamlit web-app.

**Running the app online**

Production version (stable):
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://paperfetcher-paperfetcher-web-app-paperfetcher-app-0w0vu2.streamlitapp.com/)

Development version (latest changes, can be unstable):
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://paperfetcher-paperfetcher-web-app-paperfetcher-app-devel-nzqpi2.streamlitapp.com/)


**Running the app locally**

If you have a working installation of Python 3.7+ and pip, type the following commands in Terminal to run this app:

```
pip install --upgrade streamlit paperfetcher
streamlit run https://raw.githubusercontent.com/paperfetcher/paperfetcher-web-app/main/paperfetcher_app.py
```

To run the development version of the app:

```
pip install --upgrade streamlit paperfetcher
streamlit run https://raw.githubusercontent.com/paperfetcher/paperfetcher-web-app/devel/paperfetcher_app.py
```

Alternatively, you can clone this repository, navigate to the repository directory in Terminal and type the following commands:

```
pip install -r requirements.txt
streamlit run paperfetcher_app.py
```

To run the development version of the app:

```
git checkout devel
pip install -r requirements.txt
streamlit run paperfetcher_app.py
```
