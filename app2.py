import os
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import google.generativeai as genai
import pdfplumber 

# Load environment variables
load_dotenv()

# Configure Google API key for Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get a response from the Gemini model
def get_gemini_response(input, data, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, data, prompt])

    # Check if candidates are available
    if hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]  # Get the first candidate
        
        # Check if the candidate has parts and extract the text from 'parts'
        if hasattr(candidate, "parts"):
            # Extract the text from each part
            parts_text = [part.text for part in candidate.parts if hasattr(part, "text")]
            return " ".join(parts_text) if parts_text else "No 'text' field found in parts"
        else:
            return "No 'parts' field found in response"
    else:
        return "No response from Gemini model"

# Function to prepare images for the model
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

# Function to extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text()  # Extract text from each page
    return full_text

# Streamlit app setup
st.set_page_config(page_title="Gemini Invoice Extractor")

st.header("Invoice Extractor")

# Input prompt from the user
input_text = st.text_input("Enter your question about the invoices:", key="input")

# Allow multiple file uploads (both images and PDFs)
uploaded_files = st.file_uploader("Choose invoice files...", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

# Initialize a list to store responses
responses = []

# Display and process uploaded files
if uploaded_files:
    for file in uploaded_files:
        if file.type in ["application/pdf"]:
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(file)
            st.write(f"Uploaded PDF: {file.name}")
            st.write("Extracted Text:")
            st.write(pdf_text)
            image_data = pdf_text
        else:
            # Display image
            image = Image.open(file)
            st.image(image, caption=f"Uploaded Image: {file.name}", use_column_width=True)
            image_data = input_image_setup([file])
        
        # Store responses for each file
        if file.type in ["application/pdf"]:
            response = get_gemini_response(input_text, image_data, "Extract information from the PDF.")
        else:
            response = get_gemini_response(input_text, image_data[0], "Extract information from the image.")
        
        # Append response to the list with file name for reference
        responses.append(f"{file.name}: {response}")
    
    # Display all responses collectively
    st.subheader("Responses for all invoices:")
    for response in responses:
        st.write(response)
