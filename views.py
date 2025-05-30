from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PDFDocument
from .forms import PDFUploadForm
from .summarizer_utils import extract_text_from_pdf, get_bert_gpt2_summary, get_gemini_summary
from django.core.exceptions import ValidationError
import os

@login_required
def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create PDFDocument instance but don't save yet
                pdf_doc = form.save(commit=False)
                pdf_doc.user = request.user
                pdf_doc.title = os.path.splitext(request.FILES['file'].name)[0]
                
                # Extract text and generate summaries
                text = extract_text_from_pdf(request.FILES['file'])
                
                if pdf_doc.summary_type == 'bert_gpt2':
                    try:
                        summaries = get_bert_gpt2_summary(text)
                        pdf_doc.bert_summary = summaries['bert_summary']
                        pdf_doc.gpt2_summary = summaries['gpt2_summary']
                    except Exception as e:
                        messages.warning(request, 'BERT/GPT-2 summarization failed. Using partial results.')
                else:  # gemini
                    try:
                        summaries = get_gemini_summary(text)
                        pdf_doc.gemini_summary = summaries['gemini_summary']
                    except Exception as e:
                        messages.warning(request, 'Gemini summarization failed. Using partial results.')
                
                # Save the document with summaries
                pdf_doc.save()
                messages.success(request, 'PDF uploaded and summarized successfully!')
                return redirect('pdf_detail', pk=pdf_doc.pk)
                
            except Exception as e:
                messages.error(request, f'Error processing PDF: {str(e)}')
    else:
        form = PDFUploadForm()
    
    return render(request, 'summarizer/upload.html', {'form': form})

class PDFListView(LoginRequiredMixin, ListView):
    model = PDFDocument
    template_name = 'summarizer/pdf_list.html'
    context_object_name = 'pdfs'
    ordering = ['-uploaded_at']
    paginate_by = 10

    def get_queryset(self):
        return PDFDocument.objects.filter(user=self.request.user).order_by('-uploaded_at')

@login_required
def pdf_detail(request, pk):
    try:
        pdf = PDFDocument.objects.get(pk=pk)
        return render(request, 'summarizer/pdf_detail.html', {'pdf': pdf})
    except PDFDocument.DoesNotExist:
        messages.error(request, 'PDF not found.')
        return redirect('pdf_list')
