import os
import json
import openai
import nest_asyncio
from llama_index.core import (
    load_index_from_storage,
    StorageContext,
    VectorStoreIndex,
    PromptTemplate,
    get_response_synthesizer,
)
from llama_parse import LlamaParse
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import SimpleDirectoryReader

# Initialize necessary settings
nest_asyncio.apply()

class LlamaCoverLetterGenerator:
    def __init__(self, openai_api_key, LLAMA_CLOUD_API_KEY, embed_folder_path, resume_path, course_data_path):
        openai.api_key = openai_api_key
        self.llama_api_key=LLAMA_CLOUD_API_KEY
        self.embed_folder_path = embed_folder_path
        self.resume_path = resume_path
        self.course_data_path = course_data_path
        self.documents = None
        self.index = None
        self.nodes = None
        self.query_engine = None
        self.llm = None
        self.embed_model = None

    def initialize_models(self):
        """Initialize LLM and embedding models."""
        try:
            self.llm = OpenAI(model="gpt-4o-mini", temperature=0.75)
            self.embed_model = HuggingFaceEmbedding(model_name="Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True)
            print("Models initialized successfully.")
        except Exception as e:
            print(f"Error initializing models: {e}")
            raise

    def load_resume(self):
        """Load and process resume PDF into documents."""
        try:
            parser = LlamaParse(api_key=self.llama_api_key, result_type="text")
            file_extractor = {".pdf": parser}
            self.documents = SimpleDirectoryReader(
                input_files=[self.resume_path], file_extractor=file_extractor
            ).load_data()
            print("Resume loaded successfully.")
        except Exception as e:
            print(f"Error loading resume: {e}")
            raise

    def split_documents_into_nodes(self, chunk_size=512, chunk_overlap=30):
        """Split documents into nodes for indexing."""
        try:
            node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            self.nodes = node_parser.get_nodes_from_documents(self.documents)
            print(f"Nodes created successfully. Total nodes: {len(self.nodes)}")
        except Exception as e:
            print(f"Error splitting documents into nodes: {e}")
            raise

    def build_or_load_index(self):
        """Build a new index or load an existing one from storage."""
        try:
            if not os.path.exists(self.embed_folder_path):
                os.makedirs(self.embed_folder_path, exist_ok=True)
                self.index = VectorStoreIndex(self.nodes, embed_model=self.embed_model)
                self.index.storage_context.persist(self.embed_folder_path)
                print("Index built and persisted successfully.")
            else:
                storage_context = StorageContext.from_defaults(persist_dir=self.embed_folder_path)
                self.index = load_index_from_storage(storage_context=storage_context)
                print("Index loaded successfully from storage.")
        except Exception as e:
            print(f"Error building or loading index: {e}")
            raise

    def setup_query_engine(self):
        """Set up the query engine with retriever and response synthesizer."""
        try:
            retriever = VectorIndexRetriever(index=self.index, similarity_top_k=5)
            qa_prompt_tmpl = (
            "Context information is below.\n"
            "---------------------\n"
            "{context_str}\\n"
            "---------------------\n"
            "Given the context information and not prior knowledge, "
            "Write the cover letter using the Pdf data and the Context string.\n"
            "If there are more than one Professors in the list, then create as many cover letters."
            "Cover letters are comprised of at least 3 \– 4 paragraphs and should be written in a manner that highlights the skills, abilities and accomplishments listed on your résumé. Additionally, the overall tone of your cover letter should be conversational and professional while relaying your enthusiasm for the organization. Your goal is to motivate the employer to read your résumé and invite you for an interview."
            "Inasmuch, the cover letter should hone in on your areas of expertise by summarizing your experience as it relates to the requirements for the job or internship for which you are applying. Be sure to use transitional words to segue from one thought and paragraph to another, and review the Course title, description and Professors thoroughly. so you’re able to customize the letter to the position and organization. Below are the essentials of a cover letter"
            "On the top left, Header, there should be My Name, My Address and Email, then Todays Date and then Professor’s Name, Professor’s Title (e.g., Professor of [Subject/Department]),then, University of Maryland\n3972 Campus Drive College Park, MD 20742\nUnited Sates"
            "Then Address the letter to the Professor. Only use “To Whom It May Concern” if you’re unable to locate this information. "
   
            "Opening Paragraph: Write an opening paragraph for a cover letter expressing interest in a Graduate Assistantships/Teaching Assistantships/Research Assistantships/Grader position for the course [Course Name]: [Course Title] at the University of Maryland. The applicant is a current {fetch the latest education from the resume(data) provided} in [Program Name] (or related field). Highlight their strong academic background, skills, and attention to detail, and explain why these qualities make them an ideal candidate for the Graduate Assistantships/Teaching Assistantships/Research Assistantships/Grader position. Additionally, mention how the {course description} aligns with the applicant's previous coursework or professional experience, as well as their ability to contribute to teaching/research/grading and assisting students."
    
            "Second Paragraph: Write the second paragraph of the cover letter, showcasing how the applicant’s skills and prior experience make them a strong fit for the Graduate Assistantships/Teaching Assistantships/Research Assistantships/Grader role. Mention specific relevant coursework, projects, or tutoring/teaching experience (if applicable) that highlights their qualifications for the position which relates to the Course Description, if its different, then make up your own in a professional manner. Explain how their skills, such as analytical thinking, attention to detail, or ability to communicate complex concepts, will help them excel in this role.\n"
    
            "Third Pararaph: Showing a genuine interest in the professor's research or course topic can make your application more compelling. Mention any specific research, project, or area of study related to the professor's work that aligns with your academic interests."

            "Fourth Parapgraph:Write the closing paragraph of the cover letter, expressing enthusiasm for the opportunity and willingness to contribute to the course. Highlight the applicant's eagerness to assist the professor and support students. "
    
            "At last, Use a professional closing and include your first and last name."
            "Query: {query_str}\n"
            "Answer: "
        )
            qa_prompt = PromptTemplate(qa_prompt_tmpl)
            response_synthesizer = get_response_synthesizer(
                llm=self.llm, text_qa_template=qa_prompt, response_mode="compact"
            )
            self.query_engine = RetrieverQueryEngine(
                retriever=retriever, response_synthesizer=response_synthesizer
            )
            print("Query engine setup successfully.")
        except Exception as e:
            print(f"Error setting up query engine: {e}")
            raise

    def generate_cover_letters(self):
        """Generate cover letters based on the course data."""
        try:
            with open(self.course_data_path, "r") as file:
                course_data = json.load(file)
            for i in course_data:
                response = self.query_engine.query(str(i))
                # print(response)
                break
            print("Cover letters generated successfully.")
            return response
        except FileNotFoundError:
            print("Course data file not found. Please check the file path.")
            raise
        except Exception as e:
            print(f"Error generating cover letters: {e}")
            raise


# Main Execution
if __name__ == "__main__":
    # Define file paths and API keys
    OPENAI_API_KEY_API_KEY = os.getenv("OPENAI_API_KEY")
    LLAMA_CLOUD_API_KEY=os.getenv("LLAMA_CLOUD_API_KEY")
    RESUME_PATH = r"E:\Web Scraping\Data\Resumes\Jiten Bhalavat Resume.pdf"
    COURSE_DATA_PATH = "Data/Outputs/course_data.json"
    EMBED_FOLDER_PATH = r"E:\Web Scraping\Data\Outputs\Embeddings"

    try:
        # Instantiate the generator class
        generator = LlamaCoverLetterGenerator(
            openai_api_key=OPENAI_API_KEY_API_KEY,
            LLAMA_CLOUD_API_KEY=LLAMA_CLOUD_API_KEY,
            embed_folder_path=EMBED_FOLDER_PATH,
            resume_path=RESUME_PATH,
            course_data_path=COURSE_DATA_PATH,
        )

        # Execute the pipeline
        generator.initialize_models()
        generator.load_resume()
        generator.split_documents_into_nodes()
        generator.build_or_load_index()
        generator.setup_query_engine()
        cover_letters = generator.generate_cover_letters()

        # Output generated cover letters
        print(cover_letters)

    except Exception as main_exception:
        print(f"An error occurred during execution: {main_exception}")
