# Pomodoro Pro — Streamlit

This is the web version of the Pomodoro Pro concept, built with **Python + Streamlit**. It includes the 25-minute work timer, 5-minute short breaks, a 15-minute break after each fourth work session, a task checklist, and monthly calendar notes.

## Run locally

Open this folder in VS Code, then run in its terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Upload `app.py` and `requirements.txt` to a GitHub repository.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py` (or its subfolder path).
4. Deploy; Streamlit installs the listed dependencies and gives you a public app URL.

The app keeps its data in Streamlit session state, so tasks and notes are temporary and belong to the current browser session. Persistent, cross-visit data would require a database.
