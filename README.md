## AutoCoverGen-Using-Testudo-Web-Scraping

Automating Cover Letter Generation and Professor Outreach 📝📧

## 🚨📄 Problem Statement:
For graduate students, securing a Research Assistantship, Graduate Assistantship, or Grader position involves reaching out to professors across multiple courses, subjects, and departments. This manual process is both time-consuming and tedious:        
  
  1.) Each course comprises multiple subjects.                       
  2.) Each subject has multiple professors.                       
  3.) Gathering professor details, subject descriptions, and crafting personalized emails and cover letters can take hours (up to 5-6 hours just for a single course).   
  
To streamline this process, AutoCoverGen automates the entire workflow—saving time and effort while ensuring a professional and personalized approach.

## 💡 Solution Overview
AutoCoverGen is a web application powered by cutting-edge technologies:

### ✍️ User Inputs:

Users provide their basic details (Course Name, Term, Level:- Undergraduate, Graduate, or both) and Upload their Resume.

### 🤖 Automated Workflow:

1.) Scraping Course Data.py: Scrapes Testudo (University of Maryland's system) to fetch subjects, professor names, subject IDs, and descriptions for the selected course.     

2.) Scraping Prof Emails.py: Retrieves the email addresses of all professors identified in Scraping Course Data.py                    

3.) CoverLetterGeneration.py: Combines user details, resume, and course descriptions to generate personalized cover letters for each professor using advanced LLMs.                  

## 📤 Output:

1.) Generates personalized cover letters for all professors.                
2.) Provides a list of professor email addresses for quick outreach.              

## ✨ Key Features 
1.) Web Scraping with Selenium: Automatically fetches subjects, professors, and their details from Testudo.🕸️🤖      
2.) PDF Parsing with LlamaParse: Reads and extracts user resume data seamlessly.📄🔍        
3.) Personalized Cover Letter Generation: Uses LlamaIndex for orchestration and OpenAI's LLM to generate tailored cover letters.        
4.) Fast and Efficient: Reduces a manual 5-6 hour task to a matter of minutes.⚡⌛        
5.) Embeddings with HuggingFace: Ensures semantic understanding and contextually accurate cover letters.🧠📊    
  					
## 🛠️Tech Stack
1. Frontend: HTML, CSS, JavaScript      
2. Backend: Python      
3. Web Scraping: Selenium      
4. LLM and Orchestration:      
		• LlamaIndex      
		• OpenAI GPT models      
		• HuggingFace embeddings      
5. PDF Processing: LlamaParse

## 📥 Installation and Setup
### Installation and Setup ⚙️

1. **Clone the Repository**:  
   Open your terminal and run the following commands:  
   ```bash
   git clone https://github.com/Jiten-Bhalavat/AutoCoverGen-Using-Testudo-Web-Scraping.git
   cd autocovergen
2. Install Dependencies:
   ```bash
   pip install -r requirements.txt  
3. Run the Application:
Once you've cloned the repository, open the `upload.html` file in your browser. You can do this by navigating to the folder where the file is located and double-clicking the `upload.html` file, or by opening it directly from your browser using `File -> Open`

4. Use the Form:
Fill in the required details (course name, intake, level, and resume) in the form, and click the Submit button to generate your cover letter.

## Screenshots/Demo
![User_Details_Demo](https://github.com/Jiten-Bhalavat/AutoCoverGen-Using-Testudo-Web-Scraping/blob/main/user_details_demo.png)

