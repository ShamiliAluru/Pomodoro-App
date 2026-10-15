import calendar
from datetime import date, datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh

WORK = 25 * 60
SHORT_BREAK = 5 * 60
LONG_BREAK = 15 * 60

st.set_page_config(page_title="Pomodoro Pro", page_icon="⏱️", layout="wide")
st.markdown(
    """
    <style>
      .block-container {max-width: 1120px; padding: 1.5rem 1.25rem 2rem;}
      h1 {letter-spacing: -.03em;}
      [data-testid="stMetricValue"] {font-size: clamp(2.6rem, 5vw, 4rem); font-variant-numeric: tabular-nums;}
      [data-testid="stMetricLabel"] {font-size: .85rem;}
      div[data-testid="stProgressBar"] > div {height: .65rem;}
      .eyebrow {font-size: .78rem; font-weight: 700; letter-spacing: .1em; color: #637381;}
      .calendar-heading {text-align: center; font-weight: 650; padding-top: .35rem;}
      div.stButton > button {border-radius: 7px;}
      /* Streamlit's default button padding clips two-digit dates in the compact calendar. */
      div[data-testid="stHorizontalBlock"] div[data-testid="column"] div.stButton > button {
        min-width: 0 !important; padding-left: .15rem !important; padding-right: .15rem !important;
        white-space: nowrap; font-size: .88rem;
      }
      @media (max-width: 1000px) { .block-container {padding-left: .75rem; padding-right: .75rem;} }
    </style>
    """,
    unsafe_allow_html=True,
)

defaults = {
    "tasks": [], "notes": {}, "mode": "WORK", "completed": 0,
    "remaining": WORK, "running": False, "last_tick": datetime.now().timestamp(),
    "month": date.today().replace(day=1), "selected_day": date.today().isoformat(),
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def sync_timer():
    now = datetime.now().timestamp()
    if not st.session_state.running:
        st.session_state.last_tick = now
        return
    elapsed = max(0, int(now - st.session_state.last_tick))
    st.session_state.last_tick = now
    remaining = st.session_state.remaining - elapsed
    while remaining <= 0:
        if st.session_state.mode == "WORK":
            st.session_state.completed += 1
            is_long = st.session_state.completed % 4 == 0
            st.session_state.mode = "LONG BREAK" if is_long else "SHORT BREAK"
            remaining += LONG_BREAK if is_long else SHORT_BREAK
        else:
            st.session_state.mode = "WORK"
            remaining += WORK
    st.session_state.remaining = remaining


def start_timer():
    st.session_state.running = True
    st.session_state.last_tick = datetime.now().timestamp()


def pause_timer():
    st.session_state.running = False


def reset_timer():
    st.session_state.running = False
    st.session_state.mode = "WORK"
    st.session_state.remaining = WORK
    st.session_state.last_tick = datetime.now().timestamp()


sync_timer()
if st.session_state.running:
    st_autorefresh(interval=1000, key="pomodoro_timer_refresh")

st.title("Pomodoro Pro")
st.caption("Focus timer · Task list · Daily notes")

timer_col, task_col, calendar_col = st.columns([1, 1, 1], gap="small")

with timer_col:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">FOCUS TIMER</div>', unsafe_allow_html=True)
        st.markdown(f"### {st.session_state.mode.title()}")
        mins, secs = divmod(max(0, st.session_state.remaining), 60)
        st.metric("Time remaining", f"{mins:02d}:{secs:02d}")
        duration = WORK if st.session_state.mode == "WORK" else (
            LONG_BREAK if st.session_state.mode == "LONG BREAK" else SHORT_BREAK
        )
        st.progress(min(1.0, max(0.0, 1 - st.session_state.remaining / duration)))
        st.caption(f"Sessions completed: **{st.session_state.completed}**")
        start_col, pause_col, reset_col = st.columns(3, gap="small")
        start_col.button("Start", on_click=start_timer, disabled=st.session_state.running, use_container_width=True)
        pause_col.button("Pause", on_click=pause_timer, disabled=not st.session_state.running, use_container_width=True)
        reset_col.button("Reset", on_click=reset_timer, use_container_width=True)

with task_col:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">YOUR PLAN</div>', unsafe_allow_html=True)
        st.subheader("Tasks")
        with st.form("add_task_form", clear_on_submit=True):
            task_text = st.text_input("New task", placeholder="What do you want to focus on?", label_visibility="collapsed")
            submitted = st.form_submit_button("＋  Add task", use_container_width=True)
        if submitted and task_text.strip():
            st.session_state.tasks.append({"text": task_text.strip(), "done": False})
            st.rerun()
        if not st.session_state.tasks:
            st.caption("Add a task to get your focus session started.")
        for i, task in enumerate(st.session_state.tasks):
            checked = st.checkbox(task["text"], value=task["done"], key=f"task_check_{i}")
            st.session_state.tasks[i]["done"] = checked

with calendar_col:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">PLAN YOUR DAYS</div>', unsafe_allow_html=True)
        st.subheader("Calendar & notes")
        month = st.session_state.month
        prev_col, label_col, next_col = st.columns([1, 4, 1])
        if prev_col.button("‹", key="previous_month", help="Previous month", use_container_width=True):
            y, m = month.year, month.month - 1
            st.session_state.month = date(y - (m == 0), 12 if m == 0 else m, 1)
            st.rerun()
        label_col.markdown(f'<div class="calendar-heading">{calendar.month_name[month.month]} {month.year}</div>', unsafe_allow_html=True)
        if next_col.button("›", key="next_month", help="Next month", use_container_width=True):
            y, m = month.year, month.month + 1
            st.session_state.month = date(y + (m == 13), 1 if m == 13 else m, 1)
            st.rerun()

        weekdays = st.columns(7, gap=None)
        for col, day_name in zip(weekdays, ["M", "T", "W", "T", "F", "S", "S"]):
            col.markdown(f"<div style='text-align:center;color:#718096;font-size:.8rem'>{day_name}</div>", unsafe_allow_html=True)
        for week in calendar.monthcalendar(month.year, month.month):
            cols = st.columns(7, gap=None)
            for col, day in zip(cols, week):
                if day == 0:
                    col.write("")
                    continue
                key = date(month.year, month.month, day).isoformat()
                has_note = bool(st.session_state.notes.get(key))
                if col.button(str(day), key=f"calendar_{key}", use_container_width=True,
                              type="primary" if st.session_state.selected_day == key or has_note else "secondary"):
                    st.session_state.selected_day = key
                    st.rerun()

        selected = st.session_state.selected_day
        picked = date.fromisoformat(selected)
        st.caption(f"Note for {picked.strftime('%B')} {picked.day}, {picked.year}")
        note_key = f"note_text_{selected}"
        if note_key not in st.session_state:
            st.session_state[note_key] = st.session_state.notes.get(selected, "")
        st.text_area("Daily note", key=note_key, height=90, placeholder="Add a note for this day…", label_visibility="collapsed")
        if st.button("Save note", key="save_note", use_container_width=True):
            note = st.session_state[note_key].strip()
            if note:
                st.session_state.notes[selected] = note
            else:
                st.session_state.notes.pop(selected, None)
            st.rerun()

st.divider()
st.caption("Your timer, tasks, and notes are kept for this browser session. To keep them across visits, connect persistent storage later.")
