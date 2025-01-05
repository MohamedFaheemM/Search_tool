# Analytics Vidhya Search Tool

Welcome to the **Analytics Vidhya Search Tool**! This is a smart search system designed to help users find the most relevant free courses on the Analytics Vidhya platform. The tool uses advanced natural language processing (NLP) techniques to provide accurate and efficient search results.

## 🚀 Live Demo
You can access the live demo of the tool here:  
[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/MohamedFaheem/Analytics_vidhya_search_tool)

---

## ✨ Features
- **Smart Search**: Find relevant courses using natural language queries.
- **Course Details**: Get detailed information about courses, including titles, descriptions, and curriculum.
- **Similar Courses**: Discover courses similar to the one you're interested in.
- **User-Friendly Interface**: Built with Gradio for an intuitive and interactive experience.

---

## 🛠️ Technologies Used
- **LangChain**: For building the Retrieval-Augmented Generation (RAG) system.
- **Hugging Face Embeddings**: For generating embeddings of course data.
- **Google Gemini**: For powering the question-answering system.
- **Chroma Vector Store**: For storing and retrieving course embeddings.
- **Gradio**: For creating the user interface and deploying the tool on Hugging Face Spaces.

---

## 🧑‍💻 How It Works
1. **Data Collection**: Course data (titles, descriptions, curriculum) is collected from the Analytics Vidhya platform.
2. **Embedding Generation**: The course data is converted into embeddings using Hugging Face's `sentence-transformers/all-MiniLM-L6-v2` model.
3. **Vector Store**: The embeddings are stored in a Chroma vector database for efficient retrieval.
4. **Search System**: Users can enter queries, and the system retrieves the most relevant courses using the RAG pipeline.
5. **User Interface**: The Gradio interface allows users to interact with the search tool seamlessly.

---

## 🖥️ How to Use
1. **Enter a Query**: Type your query in the search box (e.g., "Data Science courses").
2. **View Results**: The tool will display:
   - **Search Result**: The most relevant course based on your query.
   - **Similar Courses**: A list of courses similar to the one you searched for.
3. **Explore Courses**: Click on the course links to learn more about them on the Analytics Vidhya platform.

---

## 🛠️ Setup and Installation
If you want to run this project locally, follow these steps:

### Prerequisites
- Python 3.8 or higher
- Git
- A Google API key for Gemini (set as `GEMINI_API_KEY` in your environment variables)

### Steps
1. Clone the repository:
   ```
   git clone https://huggingface.co/spaces/MohamedFaheem/Analytics_vidhya_search_tool
   cd Analytics_vidhya_search_tool

2. Install dependencies:

```
pip install -r requirements.txt
```
3. Set up environment variables:

Create a .env file and add your Google API key:

```
Copy
GEMINI_API_KEY=your_api_key_here
```

4. Run the application:

```
python app.py
```

Open the Gradio interface in your browser and start searching!

📂 Project Structure
```
Analytics_vidhya_search_tool/
├── data/
│   ├── courses_data.json          # Course data in JSON format
│   └── vectorstore/               # Chroma vector store
├── rag_search_system.py           # Core search system logic
├── app.py                         # Gradio interface
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

🤝 Contributing
Contributions are welcome! If you'd like to improve this project, please follow these steps:

Fork the repository.

Create a new branch (git checkout -b feature/YourFeatureName).

Commit your changes (git commit -m 'Add some feature').

Push to the branch (git push origin feature/YourFeatureName).

Open a pull request.

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.
