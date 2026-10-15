# Pomodoro Pro — Streamlit

A browser version of the Tkinter Pomodoro Pro app with a focus timer, checklist, monthly calendar, and daily notes.

## Run locally

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and this README.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file path to `app.py` (or the subfolder path if you uploaded this folder inside a larger repository).
4. Deploy. Streamlit will install `requirements.txt` and provide a shareable URL.

This starter keeps data in Streamlit session state. Tasks, notes, and timer progress are not backed up across sessions or shared between users. Use a database such as Supabase or SQLite with persistent hosting if you need durable data.
