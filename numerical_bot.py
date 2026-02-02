import google.genai as genai
from google.genai import types
import pathlib
import PyPDF2

API_KEY = "YOUR API KEY "

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def solve_numerical_with_gemini(problem_text):
    client = genai.Client(api_key=API_KEY)

    prompt = f"""
You are a helpful numerical problem solver. 
Solve the following physics or math problem clearly and step-by-step. 
Explain each step in simple, short sentences so anyone can understand. 
Avoid using LaTeX or symbols like $ or **. 
Use plain text formatting with clear step numbers and a final summary.

Problem:
{problem_text}

Your answer should look like this:
Step 1: ...
Step 2: ...
...
Final Answers:
Acceleration = ...
Velocity = ...
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    output_text = ""
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            output_text += part.text.strip() + "\n"

    print("\n==============================")
    print("📘 Step-by-step Solution")
    print("==============================\n")
    print(output_text.strip())
    print("\n==============================")
    print("✅ Solution Completed")
    print("==============================\n")


def main():
    choice = input("Enter 1 to input text, 2 for PDF file: ").strip()

    if choice == "1":
        problem_text = input("Paste your numerical problem here:\n")
    elif choice == "2":
        pdf_path = input("Enter path to your PDF file: ").strip()
        problem_text = extract_text_from_pdf(pdf_path)
        print(f"\nExtracted problem text:\n{problem_text}\n")
    else:
        print("Invalid selection.")
        return

    solve_numerical_with_gemini(problem_text)


if __name__ == "__main__":
    main()
