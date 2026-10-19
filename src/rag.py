import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def inicializar_rag(pdf_path: str, persist_directory: str = "data/chroma_db"):
    """
    Inicializa o carga el vector store de Chroma utilizando embeddings locales de HuggingFace.
    Evita problemas de 404 con la API de Google y permite recuperar fragmentos de la guía.
    """
    # Usamos un modelo ligero y eficiente que se descarga automáticamente en local
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"No se encuentra el archivo PDF en la ruta: {pdf_path}")
            
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )