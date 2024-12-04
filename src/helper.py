from langchain.document_loaders import PyPDFLoader, DirectoryLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceBgeEmbeddings
import pdfplumber

# Extract data from the PDF files
def load_pdf_file(data):
    loader = DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

# Extract data from the CSV files
def load_csv_file(data):
    loader = DirectoryLoader(data, glob="*.csv", loader_cls=lambda file_path: CSVLoader(file_path, encoding='utf-8'))
    documents = loader.load()
    return documents

# Split the Data in Chunks
def text_split(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks

# Download the embeddings from Hugging Face
def download_hugging_face_embeddings():
    embeddings = HuggingFaceBgeEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    return embeddings

# Helper to extract and embed PDF content
def embed_pdf_content(pdf_file_path, embeddings, index_name, pinecone_instance):
    try:
        # Read PDF content
        with pdfplumber.open(pdf_file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        text_chunks = splitter.split_text(text)

        # Create embeddings
        embedding_model = embeddings
        embeddings_result = embedding_model.embed_documents(text_chunks)

        # Connect to Pinecone
        index = pinecone_instance.Index(index_name)

        # Save embeddings to Pinecone
        docs_to_store = [{
            'id': f"{pdf_file_path}-{i}",
            'values': embeddings_result[i],
            'metadata': {'text': text_chunks[i]}
        } for i in range(len(text_chunks))]

        index.upsert(vectors=docs_to_store)
        return "Embedding uploaded successfully."

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to extract text from images using OCR
# def extract_text_from_image(image_file):
#     try:
#         # Open the image file
#         image = Image.open(image_file)
#         # Use Tesseract to extract text from the image
#         extracted_text = pytesseract.image_to_string(image)
#         return extracted_text
#     except Exception as e:
#         return f"An error occurred while extracting text from the image: {str(e)}"
