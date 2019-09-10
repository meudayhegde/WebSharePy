#!/usr/bin/python3

from flask import Flask,render_template, send_file, send_from_directory, redirect, url_for, request
from sys import argv
from os import environ,walk,listdir, mkdir
from os.path import relpath,isdir,join, exists, getsize, getmtime
from sys import argv
from time import ctime
import json

class FileUtils():
	def __init__(self,path):
		self.path=path
		self.name = path.split('/')[-1]
		if self.name=='': self.name=path.split('/')[-2]
		self.modified=ctime(getmtime(path))
		if isdir(self.path):self.type = 'dir'
		else:
			self.type='raw'
			if '.' in self.name : self.type = self.name.split('.')[-1]
			if self.type == '':self.type='raw'
		
	def __repr__(self):
		return self.name
		
	def __str__(self):
		return self.name
		
	def get_size_string(self):
		bt_size=self.get_size()
		if(bt_size<=1024): return str(bt_size)+' Bytes'
		elif(bt_size<=1024*1024): return str(round(bt_size/1024,2))+' KB'
		elif(bt_size<=1024*1024*1024): return str(round(bt_size/(1024**2),2))+' MB'
		else: return str(round(bt_size/(1024**3),2))+' GB'
	
	def get_size(self):
		if exists(self.path) and not isdir(self.path):
			return getsize(self.path)
		return len(listdir(self.path))

class PyExplorer():
	def __init__(self,port,path,host,debug=True):
		self.app=Flask(__name__)
		self.app.config['PORT']=port
		self.app.config['PATH']=path
		self.app.config['HOST']=host
		self.app.config['CURRENT_PATH']=path
		self.app.config["CURRENT_ROUTE"]='/'
		self.debug=debug
		
		self.create_routes()
		
	
	def add_config(self,args):
		for arg in args:
			try:
				self.app.config[arg.split('=')[0]]=eval(arg.split('=')[1])
			except:
				print('Invalid argument format')
	
	def ajax_response(self,status, msg):
		status_code = "ok" if status else "error"
		return json.dumps(dict(status=status_code,msg=msg,))
	
	def create_routes(self):
		@self.app.route('/')
		def home():
			return redirect(url_for('explore'))
			
		@self.app.route('/explore/')
		def explore():
			self.app.config["CURRENT_ROUTE"]='/'
			return self.routes()
			
		@self.app.route('/explore/<path:varargs>')
		def non_root(varargs):
			self.app.config["CURRENT_ROUTE"]='/'+varargs
			return self.routes(varargs)
	
		@self.app.route('/templates/<path:varargs>')
		def styles(varargs):
			return send_file("templates/"+varargs,as_attachment=False)
		
		@self.app.route('/download/<path:varargs>')
		def download(varargs):
			path=join(self.app.config['PATH'],varargs)
			return send_from_directory(path,as_attachment=True)
		
		@self.app.route('/mkdir/<path:varargs>',methods=['POST'])
		def mk_dir(varargs):
			try:
				form=request.form
				mkdir(join(self.app.config['PATH'],varargs,form['dirname']))
				return redirect('/explore/'+varargs+'/'+form['dirname'])
			except Exception as ex:
				return '<h1>Failed to create folder '+ str(ex) +'</h1>'
				
		@self.app.route('/mkdir/',methods=['POST'])
		def make_dir():
			try:
				form=request.form
				mkdir(join(self.app.config['PATH'],form['dirname']))
				return redirect('/explore/'+form['dirname'])
			except Exception as ex:
				return '<h1>Failed to create folder '+ str(ex) +'</h1>'
			
		
		@self.app.route("/upload", methods=["POST"])
		def upload():
			"""Handle the upload of a file."""
			form = request.form

			# Is the upload using Ajax, or a direct POST by the form?
			is_ajax = False
			if form.get("__ajax", None) == "true":
				is_ajax = True

			# Target folder for these uploads.
			target = self.app.config["CURRENT_PATH"]
			try:
				if not isdir(target) and not exists(target): os.mkdir(target)
			except:
				if is_ajax:
					return self.ajax_response(False, "Couldn't create upload directory: {}".format(target))
				else:
					return "Couldn't create upload directory: {}".format(target)

			print("=== Form Data ===")
			for key, value in list(form.items()):
				print(key, "=>", value)

			for upload in request.files.getlist("file"):
				filename = upload.filename.rsplit("/")[0]
				destination = join(target, filename)
				print("Accept incoming file:", filename)
				print("Save it to:", destination)
				upload.save(destination)

			if is_ajax:
				return self.ajax_response(True, "/explore"+self.app.config["CURRENT_ROUTE"])
			else:
				return redirect("/explore"+self.app.config["CURRENT_ROUTE"])
	
	def routes(self,varargs='.'):
		path=join(self.app.config['PATH'],varargs)
		if not isdir(path) : return send_file(path,as_attachment=True)
		
		dirs=[FileUtils(join(path,dir)) for dir in listdir(path) if isdir(join(path,dir))]
		dirs.sort(key=lambda x: x.name)
		files=[FileUtils(join(path,file)) for file in listdir(path) if file not in [dir.name for dir in dirs]]
		files.sort(key=lambda x: x.name)
		disp_path=[self.app.config['PATH'].split('/')[-1]]
		disp_dict={disp_path[0]:'/'}
		if varargs != '.':
			var=varargs.split('/')
			if '' in var : var.remove('')
			disp_path+=var
			for i in range(len(var)):
				st='/'
				for k in range(i+1):
					st+=var[k]+'/'
				disp_dict[var[i]]= st
		self.app.config['CURRENT_PATH']=path
		return render_template('page.html',path=varargs,dirs=dirs,files=files,disp_dict=disp_dict,disp_path=disp_path,config=self.app.config)

	def start(self):
		self.app.run(debug=self.debug,host=self.app.config['HOST'],port=self.app.config['PORT'])
