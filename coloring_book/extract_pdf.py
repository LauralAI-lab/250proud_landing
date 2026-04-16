import pypdf

def extract_pdf_text(filepath):
    try:
        reader = pypdf.PdfReader(filepath)
        text = ""
        for page_num, page in enumerate(reader.pages):
            text += f"--- PAGE {page_num+1} ---\n"
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        print(text)
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    extract_pdf_text("lulu-book-creation-guide.pdf")
