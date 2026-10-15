import calendar
from datetime import date, datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh


WORK_SECONDS = 25 * 60
SHORT_BREAK_SECONDS = 5 * 60
LONG_BREAK_SECONDS = 15 * 60

st.set_page_config(page_title="Pomodoro Pro", page_icon="⏱️", layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1180px; padding-top: 2rem;}
    [data-testid="stMetricValue"] {font-size: 3rem;}
    .today {border: 2px solid #4f8bf9 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "notes" not in st.session_state:
    st.session_state.notes = {}
if "mode" not in st.session_state:
    st.session_state.mode = "Work"
if "completed" not in st.session_state:
    st.session_state.completed = 0
if "remaining" not in st.session_state:
    st.session_state.remaining = WORK_SECONDS
if "running" not in st.session_state:
    st.session_state.running = False
if "last_tick" not in st.session_state:
    st.session_state.last_tick = datetime.now().timestamp()
if "month" not in st.session_state:
    today = date.today()
    st.session_state.month = date(today.year, today.month, 1)
if "selected_day" not in st.session_state:
    st.session_state.selected_day = date.today().isoformat()


def advance_timer():
    now = datetime.now().timestamp()
    if not st.session_state.running:
        st.session_state.last_tick = now
        return

    elapsed = max(0, int(now - st.session_state.last_tick))
    st.session_state.last_tick = now
    remaining = st.session_state.remaining - elapsed

    while remaining <= 0:
        if st.session_state.mode == "Work":
            st.session_state.completed += 1
            st.session_state.mode = "Long break" if st.session_state.completed % 4 == 0 else "Short break"
            remaining += LONG_BREAK_SECONDS if st.session_state.mode == "Long break" else SHORT_BREAK_SECONDS
        else:
            st.session_state.mode = "Work"
            remaining += WORK_SECONDS
    st.session_state.remaining = remaining


def start_timer():
    st.session_state.running = True
    st.session_state.last_tick = datetime.now().timestamp()


def pause_timer():
    st.session_state.running = False


def reset_timer():
    st.session_state.running = False
    st.session_state.mode = "Work"
    st.session_state.remaining = WORK_SECONDS
    st.session_state.last_tick = datetime.now().timestamp()


advance_timer()
if st.session_state.running:
    st_autorefresh(interval=1000, key="pomodoro_clock")

st.title("Pomodoro Pro")
st.caption("A little focus, one session at a time.")

timer_col, tasks_col, calendar_col = st.columns([1.0, 1.25, 1.2], gap="large")

with timer_col:
    st.subheader("Focus timer")
    st.markdown(f"### {st.session_state.mode}")
    minutes, seconds = divmod(max(0, st.session_state.remaining), 60)
    st.metric("Time remaining", f"{minutes:02d}:{seconds:02d}")
    total = WORK_SECONDS if st.session_state.mode == "Work" else (
        LONG_BREAK_SECONDS if st.session_state.mode == "Long break" else SHORT_BREAK_SECONDS
    )
    st.progress(min(1.0, max(0.0, 1 - st.session_state.remaining / total)))
    st.caption(f"Sessions completed: {st.session_state.completed}")
    start_col, pause_col, reset_col = st.columns(3)
    start_col.button("Start", on_click=start_timer, use_container_width=True, disabled=st.session_state.running)
    pause_col.button("Pause", on_click=pause_timer, use_container_width=True, disabled=not st.session_state.running)
    reset_col.button("Reset", on_click=reset_timer, use_container_width=True)

with tasks_col:
    st.subheader("Tasks")
    with st.form("add_task", clear_on_submit=True):
        task_text = st.text_input("Add a task", placeholder="What do you want to focus on?")
        submitted = st.form_submit_button("Add task", use_container_width=True)
    if submitted and task_text.strip():
        st.session_state.tasks.append({"text": task_text.strip(), "done": False})
        st.rerun()

    if not st.session_state.tasks:
        st.info("Your task list is empty. Add a task to get started.")
    for index, task in enumerate(st.session_state.tasks):
        checked = st.checkbox(task["text"], value=task["done"], key=f"task_{index}")
        st.session_state.tasks[index]["done"] = checked

with calendar_col:
    st.subheader("Calendar & notes")
    nav_left, month_label, nav_right = st.columns([1, 3, 1])
    month = st.session_state.month
    if nav_left.button("‹", help="Previous month", use_container_width=True):
        st.session_state.month = date(month.year - (month.month == 1), 12 if month.month == 1 else month.month - 1, 1)
        st.rerun()
    month_label.markdown(f"**{calendar.month_name[month.month]} {month.year}**")
    if nav_right.button("›", help="Next month", use_container_width=True):
        st.session_state.month = date(month.year + (month.month == 12), 1 if month.month == 12 else month.month + 1, 1)
        st.rerun()

    for labels in ("Mo Tu We Th Fr Sa Su".split(),):
        cols = st.columns(7)
        for col, label in zip(cols, labels):
            col.caption(label)
    for week in calendar.monthcalendar(month.year, month.month):
        cols = st.columns(7)
        for col, day in zip(cols, week):
            if day:
                key = date(month.year, month.month, day).isoformat()
                label = f"{day}{' •' if key in st.session_state.notes and st.session_state.notes[key] else ''}"
                if col.button(label, key=f"day_{key}", use_container_width=True):
                    st.session_state.selected_day = key
                    st.rerun()
            else:
                col.write("")

    selected = st.session_state.selected_day
    try:
        selected_label = date.fromisoformat(selected).strftime("%B %-d, %Y")
    except ValueError:
        selected_label = selected
    # Windows does not support %-d in strftime.
    selected_date = date.fromisoformat(selected)
    selected_label = f"{selected_date.strftime('%B')} {selected_date.day}, {selected_date.year}"
    st.caption(f"Note for {selected_label}")
    note_value = st.text_area("Daily note", value=st.session_state.notes.get(selected, ""), label_visibility="collapsed", height=100, key=f"note_{selected}")
    if st.button("Save note", key="save_note", use_container_width=True):
        if note_value.strip():
            st.session_state.notes[selected] = note_value.strip()
        else:
            st.session_state.notes.pop(selected, None)
        st.rerun()

st.divider()
st.caption("Tasks, timer progress, and notes are held in this browser session. Add persistent storage if you want data to survive a new session.")
