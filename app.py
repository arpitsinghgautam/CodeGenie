import streamlit as st
import google.generativeai as genai
import time
import random
from e2b_code_interpreter import CodeInterpreter
import os
import base64

st.set_page_config(page_title="CodeGenie", page_icon="💻")
image_file = 'static/wallpaper1.jpg'

with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )


# Function to clean Gemini output
def clean_gemini_output(generated_code):
    code_start_index = generated_code.find("```python") + len("```python")
    code_end_index = generated_code.find("```", code_start_index)
    code = generated_code[code_start_index:code_end_index].strip()
    return code

# Main function to execute code
def execute_code(code):
    with CodeInterpreter(api_key=os.environ.get("E2B_API_KEY")) as sandbox:
        try:
            execution = sandbox.notebook.exec_cell(code)
            st.write("Inside execute_function")
            st.code(execution.output, language="python")
            return execution.output
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return str(e)

st.set_page_config(page_title="CodeGenie", page_icon="💻")
st.title("CodeGenie")
st.caption("Your AI Coding Assistant Chatbot Powered by E2B Code Interpreter SDK")

if "app_key" not in st.session_state:
    app_key = st.text_input("Please enter your Gemini API Key", type='password')
    if app_key:
        st.session_state.app_key = app_key

if "history" not in st.session_state:
    st.session_state.history = []

try:
    genai.configure(api_key=st.session_state.app_key)
except AttributeError as e:
    st.warning("Please Put Your Gemini API Key First")

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=st.session_state.history)

with st.sidebar:
    if st.button("Clear Chat Window", use_container_width=True, type="primary"):
        st.session_state.history = []
        st.rerun()

for message in chat.history:
    role = "assistant" if message.role == 'model' else message.role
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

if "app_key" in st.session_state:
    if prompt := st.chat_input(""):
        prompt = prompt.replace('\n', ' \n')
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                full_response = ""
                for chunk in chat.send_message(prompt, stream=True):
                    word_count = 0
                    random_int = random.randint(5, 10)
                    for word in chunk.text:
                        full_response += word
                        word_count += 1
                        if word_count == random_int:
                            time.sleep(0.05)
                            message_placeholder.markdown(full_response + "_")
                            word_count = 0
                            random_int = random.randint(5, 10)
                    message_placeholder.markdown(full_response)
            except genai.types.generation_types.BlockedPromptException as e:
                st.exception(e)
            except Exception as e:
                st.exception(e)
            st.session_state.history = chat.history

        if "```python" in full_response:
          code = clean_gemini_output(full_response)

          if "executed_code" not in st.session_state:
            st.session_state.executed_code = False

          if "downloaded_code" not in st.session_state:
            st.session_state.downloaded_code = False

          col1, col2 = st.columns(2)
          with col1:
              execute_button_clicked = st.button("Execute Code")
              if execute_button_clicked:
                  output = execute_code(code)
                  st.code(code, language="python")  # Display the code
                  st.write(output)  # Display the output using st.write
                  st.session_state.executed_code = True

          with col2:
              download_button_clicked = st.button("Download Code")
              if download_button_clicked:
                  with open("generated_code.py", "w") as f:
                      f.write(code)
                  # Send the file for download
                  st.download_button(
                      label="Download Code",
                      data=code,
                      file_name="generated_code.py",
                      mime="text/plain",
                  )
                  st.session_state.downloaded_code = True