from django.shortcuts import render,redirect
#from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from .models import Document
from .forms import PostForm
from django.http import HttpResponse
from django.contrib import messages
from PyPDF2 import PdfFileReader,PdfFileWriter
from pdf2image import convert_from_path
import os,shutil,csv
import cv2
import subprocess,sys
import numpy as np

dest_pdf = "/home/ieshaan/Desktop/Python/Django/document/ind_pdf/"

dest_png = "/home/ieshaan/Desktop/Python/Django/document/media/ind_png/"

pdfs_norm = "/home/ieshaan/Desktop/Python/Django/document/media/pdfs"

cropped_folder = "/home/ieshaan/Desktop/Python/Django/document/media/cropped_png/"

src_label = "/home/ieshaan/Desktop/Python/Misc/DocumentClassificationExercise/CSV_Folder/tensorflow-for-poets-2/scripts/label_image.py"
src_graph = "/home/ieshaan/Desktop/Python/Misc/DocumentClassificationExercise/CSV_Folder/tensorflow-for-poets-2/tf_files/retrained_graph.pb"

classes = []
img_list =[]
folder = []
main_csv = []

Encoder = {
"a":"Aadhar","b":"Community and Birth Certificate","c":"Marksheet","d":"Bonafide/Study and Conduct",
"e":"Income Certificate","f":"National Food Security Card","g":"Others","h":"Caste Certificate",
"i":"Blank Document","j":"EBC Certificate","k":"EBC application"}

def post_create(request):
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit = False)
		instance.save()
		folder.append(str(instance))
		try:
			os.makedirs(cropped_folder+folder[0])
		except:
			pass
		#print(type(instance.pdf)
		inputpdf = PdfFileReader(instance.pdf.open())
		for k in range(inputpdf.numPages):
			temp = []

			output = PdfFileWriter()
			output.addPage(inputpdf.getPage(k))
			f_name = dest_pdf + str(instance) + '-page-' + str(k+1) + '.pdf'
			with open(f_name, "wb") as outputStream:
				output.write(outputStream)
			page = convert_from_path(f_name,dpi = 100)

			fname = dest_png + str(instance) + '-page-' + str(k+1) + '.png'

			#print("\n\nIMAGES ARE SPLIT\n\n")
			# Cropping the image
			page[0].save(fname,'PNG')
			img =  cv2.imread(fname)
			fn=crop(img,str(instance),k,cropped_folder+str(instance))
			#print("\n\nIMAGES ARE CROPPED\n\n")

			# Apply the model
			#print("\n\nRUNNING THE MODEL\n\n")			
			command = "python3 {} --graph={} --image={}".format(src_label,src_graph,fn)
			
			test = subprocess.Popen(command,shell = True,stdout=subprocess.PIPE)

			output,err = test.communicate()
			output = output.decode("utf-8")
			output = output.split('\n')
			#print(output)
			f = fn.split('/')
			img_list.append(str(f[-1]))

			temp.append(str(f[-1]))
			s = output[3]
			c = s[0]
			temp.append(c)

			f = s[s.find("(")+1:s.find(")")]
			num = f.split('=')[1]

			temp.append(num)
			
			if(float(num)>0.9):
				temp.append("Valid")
			else:
				temp.append("ValidationRequired")

			main_csv.append(temp)
			#classes.append(output[3])
			classes.append(Encoder[c])
			#classes.append(Encoder[int(output[3].split()[0])])

		for file in os.listdir(pdfs_norm):
			f_path = os.path.join(pdfs_norm,file)
			try:
				if os.path.isfile(f_path):
					os.unlink(f_path)
			except Exception as e:
				pass

		for file in os.listdir(dest_pdf):
			f_path = os.path.join(dest_pdf,file)
			try:
				if os.path.isfile(f_path):
					os.unlink(f_path)
			except Exception as e:
				pass	
		for file in os.listdir(dest_png):
			f_path = os.path.join(dest_png,file)
			try:
				if os.path.isfile(f_path):
					os.unlink(f_path)
			except Exception as e:
				pass

		with open(cropped_folder+str(instance)+'/data.csv','w') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerows(main_csv)
		csvFile.close()
		
		messages.success(request,"Success!")

		# redirect() to a page 
		return redirect('/after/')
		#return HttpResponse("<h1>Done successfully</h1>")
	context = {"form":form}
	return render(request,'up_conv/base.html',context)

def gallery(request):
	path = cropped_folder
	tagged_list =[]
	print("\nInside gallery")
	print(img_list)
	print(len(img_list))
	for i in range(len(img_list)):
		temp = []
		tagged_list.append(img_list[i])
		tagged_list.append(classes[i])
		#tagged_list.append('ABC')
	return render(request, 'up_conv/gallery.html', {'images':tagged_list,'folder_name':folder[0]})

def crop(img,fname,count,dest):
	gray_seg = cv2.Canny(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY),0,25)
	pts = np.argwhere(gray_seg>0)
	try:
		y1,x1 = pts.min(axis = 0)
		y2,x2 = pts.max(axis = 0)
		cropped = img[y1:y2,x1:x2]
		fn = dest+ '/' + fname+ str(count) + '-c.png'
		cv2.imwrite(fn, cropped, [int(cv2.IMWRITE_PNG_COMPRESSION),9])
		return fn

	except ValueError:
		fn = dest+ '/' + fname + str(count) + '-nc.png'
		cv2.imwrite(fn, img, [int(cv2.IMWRITE_PNG_COMPRESSION),9])
		return fn


'''

		for file in os.listdir(cropped_folder):
			f_path = os.path.join(cropped_folder,file)
			folder_name = DATA+str(instance)
			try:
				os.makedirs(folder_name)
			except:
				pass
			print(f_path)
			try:
				if os.path.isfile(f_path):
					shutil.move(f_path,folder_name+'/'+file)
			except Exception as e:
				print(e)		
		'''