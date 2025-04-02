import random
import streamlit as st
from prepare import game
from arabic_support import support_arabic_text

def initialize_session():
    st.session_state.wrong            = 0
    st.session_state.correct          = 0
    st.session_state.skipped          = 0
    st.session_state.current_question = None
    st.session_state.current_date     = None
    st.session_state.current_answer   = None
    st.session_state.current_message  = None
    st.session_state.guessed          = False
    st.session_state.uploaded         = False
    st.session_state.show_feedback    = False
    st.session_state.answered_once    = False 

@st.cache_data 
def load_questions(file):
    return game(file)

def display_form(options):
    form = st.form("question")
    
    chat = form.chat_message(name="user")
    chat.write(st.session_state.current_message)   
    chat.caption(f"**{st.session_state.current_date}**")
    selection = form.pills("**Time to guess - Who's texting? 📱👀**", [option.upper() for option in options], key="selection")
    submit_btn = form.form_submit_button("GUESS!", type="primary", use_container_width=True, disabled=st.session_state.guessed)
    return form, selection, submit_btn

def main():
    if "current_question" not in st.session_state:
        initialize_session()

    st.subheader("🕵️ WhatsApp Detective")

    upload_tab, game_tab = st.tabs(["Upload Chat", "Guess Sender"])

    with upload_tab:
        uploaded_chat = st.file_uploader(label="**Upload a WhatsApp chat .txt file and start guessing the senders! 🕵️‍♀️💬**", type="txt", on_change=initialize_session)
        if uploaded_chat:
            st.session_state.uploaded = True
            questions, options = load_questions(uploaded_chat)
            selected_senders = st.multiselect("Select senders to filter", options=options, default=options, on_change=initialize_session)
            filtered_questions = [q for q in questions if q[1] in selected_senders]

    with game_tab:
        if st.session_state.uploaded:

            if st.session_state.current_question is None and filtered_questions:
                st.session_state.current_question = random.sample(filtered_questions, 1)[0]
                st.session_state.current_date = st.session_state.current_question[0]
                st.session_state.current_answer = st.session_state.current_question[1]
                st.session_state.current_message = st.session_state.current_question[2]

            left, right = st.columns(2, vertical_alignment="bottom")

            arabic = left.checkbox("ARABIC/RTL TEXT?")
            if arabic:
                support_arabic_text(components=["markdown"])
            else:
                support_arabic_text(components=[])

            if right.button("NEW MESSAGE", use_container_width=True):
                if not st.session_state.guessed:
                    st.session_state.skipped += 1
                st.session_state.guessed = False
                st.session_state.show_feedback = False
                st.session_state.answered_once = False
                st.session_state.current_question = random.sample(filtered_questions, 1)[0]
                st.session_state.current_date = st.session_state.current_question[0]
                st.session_state.current_answer = st.session_state.current_question[1]
                st.session_state.current_message = st.session_state.current_question[2]
                st.session_state["selection"] = None
                st.rerun()

            form, selection, submit_btn = display_form(selected_senders)

            if submit_btn:
                if not selection:
                    form.warning("You Didn't Guess".upper(), icon="⚠️")
                else:
                    st.session_state.guessed = True
                    if selection == st.session_state.current_answer.upper():
                        if not st.session_state.answered_once:
                            st.session_state.correct += 1
                            st.session_state.answered_once = True
                        st.session_state.feedback_message = f" Correct! It Was: **{st.session_state.current_answer}**.".upper()
                        st.session_state.feedback_type = "success"
                    else:
                        if not st.session_state.answered_once:
                            st.session_state.wrong += 1
                            st.session_state.answered_once = True
                        st.session_state.feedback_message = f" Wrong! It Was: **{st.session_state.current_answer}**.".upper()
                        st.session_state.feedback_type = "error"
                    st.session_state.show_feedback = True
                    st.rerun()

            if st.session_state.show_feedback:
                if st.session_state.feedback_type == "success":
                    form.success(st.session_state.feedback_message, icon="🎉")
                else:
                    form.error(st.session_state.feedback_message, icon="😔")

                st.session_state.show_feedback = False

            _, col2, col3, col4, _ = st.columns(5)
            col2.metric("Correct", st.session_state.correct)
            col3.metric("Wrong", st.session_state.wrong)
            col4.metric("Skipped", st.session_state.skipped)

if __name__ == "__main__":
    main()