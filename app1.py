from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google API key for Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, images, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    responses = []
    
    for image in images:
        response = model.generate_content([input, image, prompt])
        
        if response and hasattr(response, "candidates"):
            # Retrieve the first candidate's text (if available)
            if response.candidates:
                responses.append(response.candidates[0].content)
            else:
                responses.append("No candidates found in response.")
        else:
            responses.append("No response from Gemini model.")
    
    return responses

def input_image_setup(uploaded_files):
    image_parts = []
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            # Read the file into bytes
            bytes_data = uploaded_file.getvalue()
            image_parts.append({
                "mime_type": uploaded_file.type,
                "data": bytes_data
            })
    return image_parts

# Initialize Streamlit app
st.set_page_config(page_title="Invoice Extractor")
st.header("Invoice Extractor for multiple images")

# Input prompt from the user
input_text = st.text_input("Input Prompt:", key="input")

# Allow multiple image uploads
uploaded_files = st.file_uploader("Choose invoice images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Display uploaded images
if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file)
        st.image(image, caption=f"Uploaded Image: {file.name}", use_column_width=True)

# Submit button to start processing
submit = st.button("Tell me about the images")

input_prompt = """
You are an expert in understanding invoices.
You will receive input images as invoices &
you will have to answer questions based on the input image.
"""

# Process each uploaded invoice if the submit button is clicked
if submit and uploaded_files:
    # Prepare the image data
    image_data = input_image_setup(uploaded_files)
    
    # Generate responses for each image
    responses = get_gemini_response(input_prompt, image_data, input_text)
    
    # Display responses
    st.subheader("Responses for each invoice:")
    for idx, response in enumerate(responses):
        st.write(f"Invoice {idx + 1}:")
        st.write(response)
