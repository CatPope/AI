import streamlit as st
import time

message = "안녕하세요!"
with st.empty():
    full_message = ""
    for c in message:
        full_message +=c
        st.write(full_message)
        time.sleep(0.2)
st.button("Rerun")