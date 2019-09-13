def empty_method(*arg):
	pass

def __install__(package):
	__import__('subprocess').call([__import__('sys').executable, "-m", "pip", "install", package])

def safe_import(name):
	try:
		module=__import__(name)
		return module
	except ModuleNotFoundError as ex:
		if input('module',name,'not installed, do you want to install?(y/n): ').toupper()=='Y':
			__install__(name)
			return safe_import(name)

def safe_import_attr(module,*attrs):
	ret_attrs=[]
	for attr in attrs:
		ret_attrs.append(getattr(safe_import(module),attr))
	return ret_attrs
