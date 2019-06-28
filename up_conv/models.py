from django.db import models


class Document(models.Model):
	pdf = models.FileField(null=True,blank=True,upload_to = 'pdfs/')
	Application_ID = models.CharField(max_length = 100)
 
	def __str__(self):
		return self.Application_ID