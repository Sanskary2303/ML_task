import pytesseract
from pytesseract import Output
from PIL import Image
import io
import fitz  # PyMuPDF

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Path to your PDF file
pdf_path = 'a.pdf'

# Load the PDF document
pdf_document = fitz.open(pdf_path)

# Initialize the list to store extracted text
extracted_text = []

# Loop through each page and perform OCR
for page_number in range(pdf_document.page_count):
    page = pdf_document.load_page(page_number)
    img_bytes = page.get_pixmap().get_png_data()
    img = Image.open(io.BytesIO(img_bytes))

    # Perform OCR with character-level information
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1 hocr'
    hocr_output = pytesseract.image_to_data(img, output_type=Output.HOCR, config=custom_config)

    for i, line in enumerate(hocr_output.splitlines()):
        if 'bbox' in line and 'ocrx_word' in line:
            bbox = line.split('bbox ')[1].split(';')[0]
            x, y, w, h = map(int, bbox.split(' '))
            text = line.split('>')[1].split('<')[0]
            extracted_text.append({'text': text, 'x': x, 'y': y, 'width': w, 'height': h, 'page': page_number + 1})

# Close the PDF document
pdf_document.close()

# Sort extracted text by page number and y-coordinate for maintaining order
extracted_text.sort(key=lambda item: (item['page'], item['y']))

def generate_html_markup(extracted_text):
    html_markup = '<html><body>'

    for item in extracted_text:
        text = item['text']
        x, y, w, h = item['x'], item['y'], item['width'], item['height']
        span_style = f'position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px;'

        # Post-processing to identify bold and underlined text
        if 'bold' in text.lower():
            span_style += ' font-weight: bold;'
        if 'underline' in text.lower():
            span_style += ' text-decoration: underline;'

        span = f'<span style="{span_style}">{text}</span>'
        html_markup += span

    html_markup += '</body></html>'
    return html_markup

# Generate HTML markup
generated_markup = generate_html_markup(extracted_text)

# Save the generated markup to an HTML file
with open('formatted_text.html', 'w', encoding='utf-8') as html_file:
    html_file.write(generated_markup)
