import json
import os
from typing import List, Dict
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
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
        """Set up the QA chain with Gemini"""
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("Google API key not found in environment variables")

        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0,
            convert_system_message_to_human=True,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        
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
        
        try:
            # Check if the query is related to courses
            if not self._is_course_related(query):
                return {
                    "Search Result": "Please enter a query related to courses.",
                    "Similar Courses": []
                }

            # Run the QA chain
            result = self.qa_chain.run(query)
            similar = self.similar_courses(query, n=3)
            return {
                "Search Result": result,
                "Similar Courses": similar
            }
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return {
                "Search Result": "An error occurred while processing your query.",
                "Similar Courses": []
            }

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

    def _is_course_related(self, query: str) -> bool:
        """Check if the query is related to courses"""
        # Add keywords or logic to determine if the query is course-related
        course_keywords = ["course", "learn", "tutorial", "class", "training", "education"]
        return any(keyword in query.lower() for keyword in course_keywords)