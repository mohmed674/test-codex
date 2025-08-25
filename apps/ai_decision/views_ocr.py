# ai_decision/views_ocr.py
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from django.shortcuts import render
from django.core.files.uploadedfile import InMemoryUploadedFile
from .forms import OCRUploadForm
from apps.accounting.models import PurchaseInvoice

def extract_text_from_image(image_file: InMemoryUploadedFile) -> str:
    image = Image.open(image_file)
    return pytesseract.image_to_string(image, lang='ara+eng')

def extract_text_from_pdf(pdf_file: InMemoryUploadedFile) -> str:
    images = convert_from_bytes(pdf_file.read())
    return "\n".join([pytesseract.image_to_string(img, lang='ara+eng') for img in images])

def ocr_upload_view(request):
    text_result = None
    form = OCRUploadForm()
    if request.method == 'POST':
        form = OCRUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            if uploaded_file.name.endswith('.pdf'):
                text_result = extract_text_from_pdf(uploaded_file)
            else:
                text_result = extract_text_from_image(uploaded_file)
    return render(request, 'ai_decision/ocr_upload.html', {
        'form': form,
        'text_result': text_result
    })
