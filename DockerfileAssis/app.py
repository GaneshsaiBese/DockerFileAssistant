import streamlit as st
import openai
from prompts import get_prompt
from prompts import get_dockerfile_analysis_prompt
from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="Dockerfile Generator with AI")
st.title("Auto Dockerfile Generator")
user_input = st.text_area("Describe your app:", placeholder="e.g. Node.js app with MongoDB, expose port 3000")
requirements_text = st.text_area(
   "Paste your requirements.txt content (optional)",
   placeholder="e.g. Flask\ngunicorn\nrequests",
   height=150
)

if st.button("Generate Dockerfile"):
   # Check if user pasted a Dockerfile
   dockerfile_indicators = ["from ", "workdir", "copy", "cmd", "run ", "expose"]
   if any(k in user_input.lower() for k in dockerfile_indicators):
       st.info("Looks like you've pasted a Dockerfile. Let me analyze it for you!")
       from prompts import get_dockerfile_analysis_prompt
       feedback_prompt = get_dockerfile_analysis_prompt(user_input)
       try:
           response = openai.ChatCompletion.create(
               model="gpt-3.5-turbo",
               messages=[
                   {"role": "system", "content": "You are a Dockerfile analysis assistant."},
                   {"role": "user", "content": feedback_prompt}
               ],
               temperature=0.3
           )
           analysis = response["choices"][0]["message"]["content"]
           st.subheader(" Dockerfile Review:")
           st.markdown(analysis)
       except Exception as e:
           st.error(f"Could not analyze Dockerfile: {str(e)}")
       st.stop()  
   # Else: generate Dockerfile
   else:
       with st.spinner("Generating Dockerfile..."):
           try:
               response = openai.ChatCompletion.create(
                   model="gpt-3.5-turbo",
                   messages=[
                       {"role": "system", "content": "You are a helpful DevOps assistant."},
                       {"role": "user", "content": get_prompt(user_input, requirements_text)}
                   ],
                   temperature=0.4
               )
               dockerfile_code = response["choices"][0]["message"]["content"]
               st.code(dockerfile_code, language='dockerfile')
               with open("Dockerfile", "w") as f:
                   f.write(dockerfile_code)
               st.success(" Dockerfile saved as 'Dockerfile'.")
           except Exception as e:
               st.error(f" Error: {str(e)}")


