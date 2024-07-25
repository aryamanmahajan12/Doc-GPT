from django.shortcuts import render
import pdfplumber
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.http import JsonResponse,HttpResponse
from .forms import PDFUploadForm
from .models import PDFDocument


# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


def home(request):
    return HttpResponse("Welcome to the Home Page!")


def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_document = form.save()
            pdf_path = pdf_document.file.path

            # Read and parse PDF into chunks
            with pdfplumber.open(pdf_path) as pdf:
                chunks = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        chunks.extend(text.split('\n'))

            # Convert chunks to vector embeddings
            embeddings = model.encode(chunks)

            request.session['chunks'] = chunks
            request.session['embeddings'] = embeddings.tolist()  # Convert numpy array to list for JSON serialization

            print("Chunks stored in session:", request.session.get('chunks'))
            print("Embeddings stored in session:", request.session.get('embeddings'))

            return JsonResponse({'status': 'PDF processed and embeddings created.'})

    else:
        form = PDFUploadForm()
    return render(request, 'upload.html', {'form': form})

def query_pdf(request):
    query = request.GET.get('query')
    k = int(request.GET.get('k', 5))  # Default to top 5 results

    if query and 'embeddings' in request.session:
        query_embedding = model.encode([query])[0]
        embeddings = np.array(request.session['embeddings'])

        # Calculate cosine similarity
        similarities = cosine_similarity([query_embedding], embeddings)[0]
        top_k_indices = similarities.argsort()[-k:][::-1]

        chunks = request.session['chunks']
        top_k_chunks = [chunks[idx] for idx in top_k_indices]

        return JsonResponse({'query': query, 'results': top_k_chunks})

    print("Query:", query)
    print("Embeddings in session:", request.session.get('embeddings'))

    return JsonResponse({'error': 'Invalid query or no embeddings found.'})
