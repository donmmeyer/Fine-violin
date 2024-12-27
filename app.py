from flask import Flask, render_template, request
from openai import OpenAI
import os
from datetime import datetime

# Set your OpenAI API key
#openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Ensure the log folder exists
LOG_FOLDER = "log"
os.makedirs(LOG_FOLDER, exist_ok=True)

def get_context():
    """Read context from a text file."""
    try:
        with open("context.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "No context available."




def log_interaction(question, answer):
    """Log the question and answer to a dated file in the log folder."""
    try:
        # Create a log file named after the current date
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file_path = os.path.join(LOG_FOLDER, f"{date_str}.txt")
        
        # Append the interaction to the log file
        with open(log_file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] Question: {question}\n")
            log_file.write(f"[{timestamp}] Answer: {answer}\n\n")
    except Exception as e:
        print(f"Error logging interaction: {e}")

def ask_gpt_mini(question):
    """Function to query the OpenAI gpt-4o-mini model with context."""

    try:
        context = ( "Answer the given question using the context of the business Fein Violins in Minneapolis and music in general including violins, violas, cello, bows... and if the answer is not contained within the business of Fein violins and music in general, say 'I don't know'."
            + get_context()
        )
        client = OpenAI()
        # Use the context and user question in the prompt
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ]
        )
        # Extract and return the model's response
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    if request.method == "POST":
        question = request.form.get("question")
        if question:
            response = ask_gpt_mini(question)
            # Log the interaction
            log_interaction(question, response)
    return render_template("index.html", response=response)

@app.route("/answer", methods=["GET"])
def answer():
    query = request.args.get("query", "").strip()
    if not query:
        return "Error: No query provided.", 400

    # Get the response from the GPT model
    response = ask_gpt_mini(query)
    
    # Log the interaction
    log_interaction(query, response)
    
    return response


if __name__ == "__main__":
    app.run(debug=True)
