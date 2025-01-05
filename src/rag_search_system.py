import json
import os
from typing import List, Dict
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourseSearchSystem:
    def __init__(self):
        # Initialize embeddings and text splitter
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        self.vector_store = None
        self.qa_chain = None

    def load_course_data(self, file_path: str) -> List[Document]:
        """Load and process course data into documents"""
        logger.info("Loading course data...")
        with open(file_path, 'r', encoding='utf-8') as f:
            courses = json.load(f)

        documents = []
        for course in courses:
            # Combine course information into a single text
            content = f"""
            Title: {course['title']}
            Description: {course['description']}
            Instructor: {course['instructor']}
            Price: {course['price']}
            Curriculum: {' | '.join(course['curriculum'])}
            URL: {course['url']}
            """
            
            # Create document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "title": course['title'],
                    "url": course['url'],
                    "price": course['price'],
                    "instructor": course['instructor']
                }
            )
            documents.append(doc)

        logger.info(f"Loaded {len(documents)} course documents")
        return documents

    def create_vector_store(self, documents: List[Document]):
        """Create and persist vector store"""
        logger.info("Creating vector store...")
        
        # Split documents into chunks
        texts = self.text_splitter.split_documents(documents)
        logger.info(f"Split into {len(texts)} chunks")

        # Create and persist vector store
        self.vector_store = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory="data/vectorstore"
        )
        self.vector_store.persist()
        logger.info("Vector store created and persisted")

    def setup_qa_chain(self):
        """Set up the QA chain with OpenAI"""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OpenAI API key not found in environment variables")

        # Use ChatOpenAI instead of OpenAI for better results
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
        )

    def search_courses(self, query: str) -> Dict:
        """Search courses based on query"""
        if not self.qa_chain:
            raise ValueError("QA chain not initialized. Run setup_qa_chain first.")

        logger.info(f"Searching for: {query}")
        result = self.qa_chain.run(query)
        return result

    def similar_courses(self, course_title: str, n: int = 3) -> List[Dict]:
        """Find similar courses based on title"""
        logger.info(f"Finding courses similar to: {course_title}")
        results = self.vector_store.similarity_search(
            course_title,
            k=n
        )
        return [
            {
                "title": doc.metadata.get("title"),
                "url": doc.metadata.get("url"),
                "price": doc.metadata.get("price"),
                "instructor": doc.metadata.get("instructor")
            }
            for doc in results
        ]

def main():
    # Initialize the search system
    search_system = CourseSearchSystem()
    
    # Load and process course data
    documents = search_system.load_course_data("data/courses_data.json")
    
    # Create vector store
    search_system.create_vector_store(documents)
    
    # Set up QA chain
    search_system.setup_qa_chain()
    
    # Example searches
    logger.info("\nTesting search functionality:")
    
    # Search for a specific topic
    result = search_system.search_courses(
        "What courses are available for machine learning beginners?"
    )
    logger.info(f"\nSearch result: {result}")
    
    # Find similar courses
    similar = search_system.similar_courses("Python for Data Science")
    logger.info(f"\nSimilar courses: {similar}")

if __name__ == "__main__":
    main()