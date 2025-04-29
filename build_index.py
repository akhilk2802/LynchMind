from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Load and split documents
loader = Docx2txtLoader("Introduction_to_Data_and_Data_Science_3.docx")
docs = loader.load()

splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(docs)

# Embed and persist
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
persist_dir = "chroma_db"

vectorstore = Chroma.from_documents(
    documents=split_docs,
    embedding=embedding,
    persist_directory=persist_dir
)

vectorstore.persist()
print("✅ Index built and saved!")
