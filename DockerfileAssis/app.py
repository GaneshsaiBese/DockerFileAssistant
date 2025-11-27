import streamlit as st
from openai import AzureOpenAI
from prompts import get_prompt, get_dockerfile_analysis_prompt
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import traceback
# Logging Setup
logging.basicConfig(
   filename='activity.log',
   level=logging.INFO,
   format='%(asctime)s - %(levelname)s - %(message)s',
   datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger()
def log_input(user_input, mode):
   logger.info(f"Mode: {mode} | Input: {user_input.strip()[:50]}...")
def log_error(error_message, stack_trace):
   logger.error(f"Error: {error_message}\nStack Trace: {stack_trace}")
# Load env
load_dotenv()
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
client = AzureOpenAI(
   azure_endpoint=AZURE_OPENAI_ENDPOINT,
   api_key=AZURE_OPENAI_API_KEY,
   api_version=OPENAI_API_VERSION
)
# 🔍 Input Classification Function
def classify_input_type(user_input, client):
   classification_prompt = f"""
Classify the following input into one of these categories:
["Dockerfile", "App Description", "Docker Compose (YAML)", "Code Snippet", "Unclear Input"]
Input:
{user_input}
Only respond with the category name.
"""
   try:
       response = client.chat.completions.create(
           model="gpt-4o-mini",
           messages=[
               {"role": "system", "content": "Classify the input type."},
               {"role": "user", "content": classification_prompt}
           ],
           temperature=0
       )
       return response.choices[0].message.content.strip()
   except Exception as e:
       log_error(str(e), traceback.format_exc())
       return "Unclear Input"
# Streamlit UI
st.set_page_config(page_title="Dockerfile Generator with AI")
st.title("🧑‍💻 Dockerfile Assistant 🌐")
user_input = st.text_area("Describe your app or paste Dockerfile:", placeholder="e.g. Node.js app with MongoDB, expose port 3000")
requirements_text = st.text_area("Paste your requirements.txt (optional)", placeholder="e.g. Flask\ngunicorn\nrequests", height=150)
if st.button("Run Assistant"):
   log_input(user_input, "Run Assistant Button Clicked")
   if not user_input.strip():
       st.error("Input cannot be empty. Please provide a valid Dockerfile or description.")
       st.stop()
   input_type = classify_input_type(user_input, client)
   logger.info(f"Detected input type: {input_type}")
   if input_type == "Dockerfile":
       st.info("You've pasted a Dockerfile. Analyzing it now...")
       feedback_prompt = get_dockerfile_analysis_prompt(user_input)
       try:
           with st.spinner("Analyzing Dockerfile..."):
               response = client.chat.completions.create(
                   model="gpt-4o-mini",
                   messages=[
                       {"role": "system", "content": "You are a Dockerfile analysis assistant."},
                       {"role": "user", "content": feedback_prompt}
                   ],
                   temperature=0.3
               )
               analysis = response.choices[0].message.content
               st.subheader("Dockerfile Review:")
               st.markdown(analysis)
               logger.info("Dockerfile analysis completed successfully.")
       except Exception as e:
           log_error(str(e), traceback.format_exc())
           st.error(f"Could not analyze Dockerfile: {str(e)}")
   elif input_type == "App Description":
       try:
           with st.spinner("Generating Dockerfile..."):
               prompt = get_prompt(user_input, requirements_text)
               response = client.chat.completions.create(
                   model="gpt-4o-mini",
                   messages=[
                       {"role": "system", "content": "You are a DevOps assistant that generates Dockerfiles."},
                       {"role": "user", "content": prompt}
                   ],
                   temperature=0.4
               )
               dockerfile_code = response.choices[0].message.content
               st.subheader("Generated Dockerfile:")
               st.code(dockerfile_code, language='dockerfile')
               st.success("Copy the Dockerfile code above or save it manually.")
       except Exception as e:
           log_error(str(e), traceback.format_exc())
           st.error(f"Error generating Dockerfile: {str(e)}")
   elif input_type == "Docker Compose (YAML)":
       st.warning("This appears to be a Docker Compose YAML file. Please provide a Dockerfile or app description.")
   elif input_type == "Code Snippet":
       st.warning("You've pasted application code. Please describe your app instead (e.g., 'Flask app on port 5000').")
   else:
       st.warning("Could not understand your input. Please try again with a clearer description or Dockerfile.")
