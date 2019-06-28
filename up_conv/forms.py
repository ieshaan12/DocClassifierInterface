from django import forms
from up_conv.models import Document

class PostForm(forms.ModelForm):
	class Meta:
		model = Document
		fields = [
			'Application_ID',
			'pdf'
		]