import tkinter as tk
from tkinter import scrolledtext
from nltk.chat.util import Chat, reflections
import re
import wikipediaapi
import requests

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(
    user_agent="YourAppName/1.0 (your@email.com)", 
    language="en"
)

# Function to search Wikipedia
def search_wikipedia(query):
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary[:500] + "..."  # Return first 500 characters
    else:
        # Try searching Wikipedia more broadly
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json"
        response = requests.get(search_url).json()
        
        if "query" in response and "search" in response["query"]:
            if len(response["query"]["search"]) > 0:
                first_result_title = response["query"]["search"][0]["title"]  # Get best matching page title
                page = wiki_wiki.page(first_result_title)
                
                if page.exists():
                    return f"Showing results for '{first_result_title}':\n" + page.summary[:500] + "..."
        
        return "Sorry, I couldn't find relevant information on Wikipedia."

# Predefined chatbot responses
pairs = [
    [r"hi|hello|hey", ["Hello! How can I assist you today?", "Hi there! How can I help you?"]],
    [r"how are you ?", ["I'm just a bot, but I'm functioning perfectly!", "I'm doing great, thanks for asking!"]],
    [r"what is your name ?", ["I'm a chatbot created to assist you.", "You can call me ChatBot!"]],
    [r"quit|bye|goodbye", ["Goodbye! Have a great day!", "Bye! Feel free to come back anytime."]],
    [r"what can you do ?", ["I can answer your questions, provide information, or search the web for you."]],
    [r"tell me about (.*)", ["I don't know much about %1, but I can look it up for you!"]],
    [r"search for (.*)", ["Let me find information about %1 for you."]],
    [r"help", ["I'm here to help! Ask me anything, or type 'search for <topic>' to find information online."]]
]

# Initialize chatbot
chatbot = Chat(pairs, reflections)

# Function to preprocess user input
def preprocess_input(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

# Function to handle user input
def send_message():
    user_input = user_entry.get()
    user_entry.delete(0, tk.END)
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, "You: " + user_input + "\n", "user_text")
    
    # Preprocess input
    processed_input = preprocess_input(user_input)
    
    # Get chatbot response
    response = chatbot.respond(processed_input)
    
    if response:
        chat_window.insert(tk.END, "ChatBot: " + response + "\n", "bot_text")
        
        # Handle dynamic Wikipedia search
        match = re.match(r"search for (.*)", processed_input)
        if match:
            query = match.group(1)
            chat_window.insert(tk.END, "ChatBot: Searching for " + query + "...\n", "bot_text")
            search_result = search_wikipedia(query)
            chat_window.insert(tk.END, "ChatBot: " + search_result + "\n", "bot_text")
    else:
        chat_window.insert(tk.END, "ChatBot: Sorry, I couldn't understand that.\n", "bot_text")
    
    chat_window.config(state=tk.DISABLED)
    chat_window.yview(tk.END)

# Create the Tkinter GUI
root = tk.Tk()
root.title("ChatBot")
root.geometry("800x600")  # Set the window size
root.configure(bg="#1e1e1e")  # Dark background

# Chat window
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, width=80, height=25, bg="#2e2e2e", fg="white", font=("Arial", 12))
chat_window.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

# Define text tags for styling
chat_window.tag_configure("user_text", foreground="#00ff00")  # Green for user input
chat_window.tag_configure("bot_text", foreground="#00bfff")   # Blue for bot response

# User input entry
user_entry = tk.Entry(root, width=50, font=("Arial", 14), bg="#3e3e3e", fg="white", insertbackground="white")
user_entry.grid(row=1, column=0, padx=20, pady=10, ipady=5)

# Send button
send_button = tk.Button(root, text="Send", command=send_message, font=("Arial", 14), bg="#00bfff", fg="white", relief="flat", width=10)
send_button.grid(row=1, column=1, padx=10, pady=10)

# Bind Enter key to send message
root.bind('<Return>', lambda event: send_message())

# Run Tkinter event loop
root.mainloop()
