#  FastAPI-backend/app/services/chatbot_service.py
import io
import logging
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Union
from fastapi import UploadFile
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from app.utils.qdrant_client import qdrant_client
from app.core.config import get_settings

# File parsing imports
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

settings = get_settings()
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------
# 🔧 Initialize models
# ----------------------------------------------------------------
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=settings.OPENAI_API_KEY,
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    openai_api_key=settings.OPENAI_API_KEY,
)

# ----------------------------------------------------------------
# 📄 FILE TEXT EXTRACTION HELPERS
# ----------------------------------------------------------------
def extract_text_from_file(file: UploadFile) -> str:
    """
    Extracts text from uploaded files.
    """
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        pdf_reader = PdfReader(file.file)
        return "\n".join([page.extract_text() or "" for page in pdf_reader.pages])

    elif filename.endswith(".docx"):
        doc = DocxDocument(file.file)
        return "\n".join([para.text for para in doc.paragraphs])

    elif filename.endswith(".txt"):
        return file.file.read().decode("utf-8")

    elif filename.endswith(".html") or filename.endswith(".htm"):
        soup = BeautifulSoup(file.file.read(), "html.parser")
        return soup.get_text(separator="\n")

    else:
        raise ValueError(f"Unsupported file type: {filename}")


# ----------------------------------------------------------------
# 🌐 WEB PAGE SCRAPING HELPERS
# ----------------------------------------------------------------
def scrape_text_from_url(url: str, depth: int = 1, max_pages: int = 5) -> List[str]:
    """
    Crawl a given website (recursively up to `depth`) and extract visible text content.
    """
    visited = set()
    texts = []

    def crawl_page(page_url, current_depth):
        if page_url in visited or len(visited) >= max_pages or current_depth > depth:
            return
        visited.add(page_url)

        try:
            response = requests.get(page_url, timeout=10)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                return

            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style", "noscript"]):
                script.extract()
            text = soup.get_text(separator="\n", strip=True)
            if text.strip():
                texts.append(text)

            # Collect internal links
            base_domain = urlparse(url).netloc
            for link_tag in soup.find_all("a", href=True):
                link = urljoin(page_url, link_tag["href"])
                if urlparse(link).netloc == base_domain:
                    crawl_page(link, current_depth + 1)

        except Exception as e:
            logger.error(f"Failed to crawl {page_url}: {e}")

    crawl_page(url, 0)
    logger.info(f"Scraped {len(texts)} pages from {url}")
    return texts


# ----------------------------------------------------------------
# 🧠 TRAINING: FILES OR WEBSITE
# ----------------------------------------------------------------
async def train_chatbot_from_files(
    company_id: int, chatbot_id: int, files: List[UploadFile]
):
    """
    Process uploaded files → extract text → embed → store in Qdrant.
    """
    collection_name = f"chatbot_{company_id}_{chatbot_id}"
    all_texts = []

    for file in files:
        try:
            text = extract_text_from_file(file)
            if text.strip():
                all_texts.append(text)
        except Exception as e:
            logger.error(f"Error extracting {file.filename}: {e}")

    if not all_texts:
        return {"error": "No valid text found in uploaded files"}

    return await _store_texts_in_qdrant(collection_name, all_texts)


async def train_chatbot_from_url(company_id: int, chatbot_id: int, url: str):
    """
    Crawl website and train chatbot from extracted text.
    """
    collection_name = f"chatbot_{company_id}_{chatbot_id}"
    texts = scrape_text_from_url(url, depth=1, max_pages=5)
    if not texts:
        return {"error": "No readable text found at the given URL."}

    return await _store_texts_in_qdrant(collection_name, texts)


# ----------------------------------------------------------------
# 💾 COMMON FUNCTION: EMBEDDINGS + STORE IN QDRANT
# ----------------------------------------------------------------
async def _store_texts_in_qdrant(collection_name: str, texts: List[str]):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [
        Document(page_content=chunk)
        for text in texts
        for chunk in text_splitter.split_text(text)
    ]

    vector_store = Qdrant.from_documents(
        docs,
        embedding=embedding_model,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        collection_name=collection_name,
    )

    logger.info(f"✅ Data embedded and stored in Qdrant collection: {collection_name}")
    return {"message": f"Chatbot trained successfully! {len(docs)} chunks stored."}


# ----------------------------------------------------------------
# 💬 CHAT: QUERY
# ----------------------------------------------------------------
async def query_chatbot(company_id: int, chatbot_id: int, query: str):
    """
    Query chatbot and return context-aware response.
    """
    collection_name = f"chatbot_{company_id}_{chatbot_id}"
    try:
        vector_store = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=embedding_model,
        )
    except Exception as e:
        logger.error(f"Collection not found: {collection_name} | {e}")
        return {"error": "Chatbot not trained yet."}

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
    )

    result = qa_chain.invoke({"query": query})
    answer = result["result"]
    sources = [doc.page_content[:150] for doc in result["source_documents"]]

    return {"answer": answer, "sources": sources}
