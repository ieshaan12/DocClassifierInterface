from django.contrib import admin
from up_conv.models import Document

class DocumentAdmin(admin.ModelAdmin):
	pass

admin.site.register(Document,DocumentAdmin)
