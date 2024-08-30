from flask import Flask, request, jsonify
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]  # Customize limits as needed
)

# Define your OpenAI key (either pass it here or set it in environment variables)
api_key = os.getenv("OPEN_AI_API_KEY") 
 

# Initialize OpenAI GPT model
llm = OpenAI(openai_api_key=api_key, temperature=0.5)

# Define a prompt template for the chatbot
template = """You are a virtual assistant for the Department of Justice, India.
Answer the user's question based on the knowledge of the Department of Justice and its services.

Question: {user_question}
"""

prompt = PromptTemplate(template=template, input_variables=["user_question"])

# Define a function to run the prompt with the model
def run_chain(user_question):
    prompt_text = prompt.format(user_question=user_question)
    response = llm.generate([prompt_text])  # Pass prompt_text as a list
    generated_text = response.generations[0][0].text  # Access the first generation's text
    return generated_text

# Define the API endpoint with rate limiting
@app.route('/ask', methods=['POST'])
@limiter.limit("2 per minute")  # Rate limit this endpoint to 5 requests per minute
def ask_question():
    user_input = request.json.get('question')
    response = run_chain(user_input)
    return jsonify({'response': response})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'response': "UP"})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
