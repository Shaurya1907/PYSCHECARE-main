import json
import logging
import os
import random
import sys
from pathlib import Path
from typing import Dict

import nltk
import numpy as np
from autocorrect import Speller
from keras.models import load_model
from nltk.stem import WordNetLemmatizer

logging.basicConfig(level=logging.ERROR)

# Resolve the absolute path dynamically
base_dir = Path(__file__).resolve().parent
python_chatbot_path = base_dir / "Python-Mental-Health-Chatbot-main" / "Python-Mental-Health-Chatbot-main"

# Check if it actually exists before altering the environment
if python_chatbot_path.exists() and python_chatbot_path.is_dir():
    sys.path.insert(0, str(python_chatbot_path))  # Using insert(0) is often safer to prioritize local modules
else:
    print(f"Warning: Chatbot dependencies directory not found at {python_chatbot_path}")
    print("Ensure the chatbot submodule is cloned correctly.")

# Make sure required NLTK packages are downloaded
try:
    nltk.download("punkt", quiet=True)
    nltk.download("wordnet", quiet=True)
    print("NLTK packages downloaded successfully")
except Exception as e:
    print(f"Error downloading NLTK packages: {e}")

# Lemmatizer for processing text
lemmatizer = WordNetLemmatizer()

# Define global variables that will be initialized in load_chatbot_model()
words = []
classes = []
model = None
intents = {}
context: Dict[str, str] = {}

def load_chatbot_model():
    """
    Load the chatbot model and necessary data files
    """
    global words, classes, model, intents
    
    try:
        # Set paths for model files
        model_path = os.path.join(python_chatbot_path, "chatbot-model.h5")
        data_path = os.path.join(python_chatbot_path, "data.json")
        intents_path = os.path.join(python_chatbot_path, "ChatbotWebsite", "static", "data", "intents.json")
        
        # Check if we're working with the provided files or the ones in the original location
        if not os.path.exists(intents_path):
            intents_path = os.path.join(os.path.dirname(__file__), "chatbot_files", "intents.json")
            model_path = os.path.join(os.path.dirname(__file__), "chatbot_files", "model.h5")
            data_path = os.path.join(os.path.dirname(__file__), "chatbot_files", "data.json")
        
        # Load intents file
        with open(intents_path) as file:
            intents = json.load(file)
        
        # Try to load existing model and data
        try:
            with open(data_path, "r") as f:
                data_dict = json.load(f)
                words = data_dict.get("words", [])
                classes = data_dict.get("classes", [])
                training = data_dict.get("training", [])
                output = data_dict.get("output", [])
            model = load_model(model_path)
            print("Chatbot model loaded successfully!")
        except FileNotFoundError as e:
            print(f"Required model file is missing: {e.filename}")
            print("You need to train the model first or provide the model files")
            return False
        except OSError as e:
            print(f"OS error occurred while loading files: {e}")
            return False
        except Exception as e:
            # If an unexpected error happens, log the full stack trace for debugging
            logging.exception(
                "An unexpected error occurred while loading the chatbot model."
            )
            return False
            
        return True
    
    except Exception as e:
        logging.exception(
            "An unexpected error occurred while initializing the chatbot."
        )
        return False

# Helper functions from the Python chatbot implementation
def clean_up_message(message):
    """Clean and tokenize the message"""
    message_word_list = nltk.word_tokenize(message)
    message_word_list = [
        lemmatizer.lemmatize(word.lower()) for word in message_word_list
    ]
    return message_word_list

def bag_of_words(message, words_list):
    """Create a bag of words from the message"""
    message_word = clean_up_message(message)
    bag = [0] * len(words_list)
    for w in message_word:
        for i, word in enumerate(words_list):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(message, ERROR_THRESHOLD=0.25):
    """Predict the intent class of the message"""
    global words, classes, model
    
    bow = bag_of_words(message, words)
    res = model.predict(np.array([bow]))[0]
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    return return_list

def get_chatbot_response(message, user_id="000"):
    """
    Get a response from the chatbot based on the input message.
    
    Args:
        message (str): The user's message
        user_id (str): Optional user ID for context tracking
    
    Returns:
        str: The chatbot's response
    """
    global words, classes, model, intents, context
    
    # Make sure model is loaded
    if model is None:
        success = load_chatbot_model()
        if not success:
            return "Sorry, the chatbot is not available at the moment."
            
    # Detect language
    lang = detect_language(message)
    if lang != 'en':
        return "I currently only speak English, but you can contact our human support team for help in other languages."

    try:
        # Apply spelling correction
        spell = Speller()
        corrected_message = spell(message)
        
        # Get predictions
        results = predict_class(corrected_message)
        
        if results:  # if results exist
            while results:  # loop through results
                for intent in intents["intents"]:  # loop through intents
                    if intent["tag"] == results[0][0]:  # if tag matches
                        if intent["tag"].lower() == "reiterate":  # if tag is reiterate
                            if context.get(user_id):  # if context exists
                                for tg in intents["intents"]:
                                    if (
                                        "context_set" in tg
                                        and tg["context_set"] == context[user_id]
                                    ):
                                        response = random.choice(tg["responses"])
                                        return str(response)
                            else:
                                response = random.choice(intent["responses"])
                                return str(response)
                        if "context_set" in intent and intent["context_set"] != "":
                            context[user_id] = intent["context_set"]
                        response = random.choice(intent["responses"])
                        return str(response)
                results.pop(0)
        
        # Default response if no matching intent
        return "I apologize if my response wasn't what you were looking for. As an AI assistant, my knowledge is limited. Is there another way I can help you?"
    
    except Exception as e:
        logging.exception(
            "An unexpected error occurred while getting the chatbot response."
        )
        return "Sorry, I'm having trouble processing your request right now."

def detect_language(text):
    """
    Detect the language of the input text.
    
    Args:
        text (str): The input text
    
    Returns:
        str: The detected language code
    """
    try:
        from langdetect import detect
        return detect(text)
    except:
        return "en"  # Default to English

def setup_chatbot():
    """
    Setup the chatbot. Wrapper around load_chatbot_model for compatibility with app.py.
    """
    return load_chatbot_model()

# Initialize the chatbot model when this module is imported
load_chatbot_model()
