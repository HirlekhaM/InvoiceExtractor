from urllib import response
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google API key for Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])

    try:
        # Extract text from the response
        if hasattr(response, "result") and hasattr(response.result, "candidates") and response.result.candidates:
            candidate = response.result.candidates[0]  # Get the first candidate
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                parts_text = [part.text for part in candidate.content.parts if hasattr(part, "text")]
                return " ".join(parts_text) if parts_text else "No 'text' field found in parts"
            else:
                return "No 'content' or 'parts' field found in candidate"
        else:
            return "No response from Gemini model or no candidates found"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    return f"An error occurred: {str(e)}"

# Function to prepare uploaded images for the model
def input_image_setup(uploaded_files):
    image_parts = []
    for uploaded_file in uploaded_files:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()
        image_parts.append({
            "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
            "data": bytes_data
        })
    return image_parts

# Streamlit app setup
st.set_page_config(page_title="Gemini Invoice Extractor")

st.header("Invoice Extractor")

# Input prompt from the user
input_text = st.text_input("Enter your question about the invoices:", key="input")

# Allow multiple image uploads
uploaded_files = st.file_uploader("Choose invoice images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Display uploaded images
if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file)
        st.image(image, caption=f"Uploaded Image: {file.name}", use_column_width=True)

# Submit button to start processing
submit = st.button("Analyze Invoices")

# Example input prompt about the task
input_prompt = """
You are an expert in understanding invoices.
You will receive input images as invoices &
you will have to answer questions based on the input image.
"""

# Process each uploaded invoice if the submit button is clicked
if submit and uploaded_files:
    # Prepare the image data
    image_data = input_image_setup(uploaded_files)
    
    # Loop through each image and generate responses
    st.subheader("Responses for each invoice:")
    for idx, img in enumerate(image_data):
        response = get_gemini_response(input_prompt, [img], input_text)
        st.write(f"Invoice {idx + 1}:")
        st.write(response)
