#!/usr/bin/python3

import logging
from flask import Flask,render_template, send_file, send_from_directory, redirect, url_for, request, make_response
from sys import argv
from os import environ,walk,listdir, mkdir
from os.path import relpath,isdir,join, exists, getsize, getmtime, sep
from sys import argv
from time import ctime
from werkzeug.utils import secure_filename
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
		self.log = logging.getLogger('pydrop')
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
			return send_file(("templates/"+varargs).replace('/',sep),as_attachment=False)
		
		@self.app.route('/download/<path:varargs>')
		def download(varargs):
			path=join(self.app.config['PATH'],varargs.replace('/',sep))
			return send_from_directory(path,as_attachment=True)
		
		@self.app.route('/mkdir/<path:varargs>',methods=['POST'])
		def mk_dir(varargs):
			try:
				form=request.form
				mkdir(join(self.app.config['PATH'],varargs.replace('/',sep),form['dirname']))
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

		@self.app.route("/upload/<path:varargs>", methods=["POST"])
		def upload_(varargs):
			return self.upload(join(self.app.config['PATH'],varargs.replace('/',sep)),varargs)
			
		@self.app.route("/upload/", methods=["POST"])
		def upload():
			return self.upload(self.app.config['PATH'],'.')
			
	def upload(self,path,route):
		file = request.files['file']
		save_path = join(path, secure_filename(file.filename))
		current_chunk = int(request.form['dzchunkindex'])

		# If the file already exists it's ok if we are appending to it,
		# but not if it's new file that would overwrite the existing one
		if exists(save_path) and current_chunk == 0:
			# 400 and 500s will tell dropzone that an error occurred and show an error
			return make_response(('File already exists', 400))

		try:
			with open(save_path, 'ab') as f:
				f.seek(int(request.form['dzchunkbyteoffset']))
				f.write(file.stream.read())
		except OSError:
			# log.exception will include the traceback so we can see what's wrong 
			self.log.exception('Could not write to file')
			return make_response(("Not sure why,"
								  " but we couldn't write the file to disk", 500))

		total_chunks = int(request.form['dztotalchunkcount'])

		if current_chunk + 1 == total_chunks:
			# This was the last chunk, the file should be complete and the size we expect
			if getsize(save_path) != int(request.form['dztotalfilesize']):
				self.log.error(f"File {file.filename} was completed, "
						  f"but has a size mismatch."
						  f"Was {getsize(save_path)} but we"
						  f" expected {request.form['dztotalfilesize']} ")
				return make_response(('Size mismatch', 500))
			else:
				self.log.info(f'File {file.filename} has been uploaded successfully')
		else:
			self.log.debug(f'Chunk {current_chunk + 1} of {total_chunks} '
						  f'for file {file.filename} complete')

		return make_response(("Chunk upload successful", 200))			
	
    
	def routes(self,varargs='.'):
		path=join(self.app.config['PATH'],varargs.replace('/',sep))
		if not isdir(path) : return send_file(path,as_attachment=True)
		
		dirs=[FileUtils(join(path,dir)) for dir in listdir(path) if isdir(join(path,dir))]
		dirs.sort(key=lambda x: x.name)
		files=[FileUtils(join(path,file)) for file in listdir(path) if file not in [dir.name for dir in dirs]]
		files.sort(key=lambda x: x.name)
		disp_path=[self.app.config['PATH'].split(sep)[-1]]
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
