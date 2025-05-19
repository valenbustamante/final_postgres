import streamlit as st

st.session_state.logged_in = False
st.session_state.user_id = ''
st.session_state.user_type = ''
st.rerun()