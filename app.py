import gradio as gr
from rag_search_system import CourseSearchSystem

def main():
    # Initialize the search system
    search_system = CourseSearchSystem()

    # Load course data
    documents = search_system.load_course_data("data/courses_data.json")

    # Create vector store
    search_system.create_vector_store(documents)

    # Set up QA chain
    search_system.setup_qa_chain()

    # Define Gradio interface
    def search(query):
        result = search_system.search_courses(query)
        return result

    # Create Gradio interface
    iface = gr.Interface(
        fn=search,
        inputs="text",
        outputs="json",
        title="Course Search System",
        description="Enter a query to find relevant courses."
    )

    # Launch the interface
    iface.launch()

if __name__ == "__main__":
    main()