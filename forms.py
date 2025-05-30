from django import forms
from .models import PDFDocument

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['file', 'summary_type']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf',
                'aria-label': 'Upload PDF file',
                'aria-describedby': 'fileHelp'
            }),
            'summary_type': forms.Select(attrs={
                'class': 'form-control',
                'aria-label': 'Select summary type'
            })
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('File size cannot exceed 10MB.')
        return file
