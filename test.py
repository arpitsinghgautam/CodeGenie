import google.generativeai as genai
from e2b_code_interpreter import CodeInterpreter
from constants import E2B_API_KEY, GEMINI_API_KEY

#GEMINI SETUP
genai.configure(api_key=GEMINI_API_KEY)

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config=generation_config)

convo = model.start_chat(history=[
])


# Loop until user decides to stop
while True:
    # Get user input or prompt for Gemini
    user_input = input("Enter your prompt: ")

    # Send the prompt to Gemini and get the generated code
    convo.send_message(user_input)
    generated_code = convo.last.text

    # Create an instance of the CodeInterpreter
    with CodeInterpreter(api_key=E2B_API_KEY) as sandbox:
        try:
            # Execute the generated code
            execution = sandbox.notebook.exec_cell(generated_code)
            # Save the code to a file if it runs successfully
            with open("generated_code.py", "a") as f:
                f.write(generated_code)
            print("Code executed successfully!")
        except Exception as e:
            # Send the error traceback to Gemini
            error_traceback = str(e)
            convo.send_message(f"Error: {error_traceback}")
            print(f"Error: {error_traceback}")

    # Update the conversation history with the generated code and any feedback or additional prompts
    convo.send_message(generated_code)

    # Ask the user if they want to continue or stop
    continue_loop = input("Do you want to continue? (y/n) ")
    if continue_loop.lower() != "y":
        break