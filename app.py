import streamlit as st
from openai import OpenAI

# Initialize client using Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("My First AI App")

user_input = st.text_input("Type something:")

if st.button("Submit") and user_input:
    with st.spinner("Thinking..."):
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=user_input
        )
        
        answer = response.output[0].content[0].text
        st.write(answer)
