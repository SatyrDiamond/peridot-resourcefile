from objects import easybinrw
from objects import peridot_datatypes
from objects.data_bytes import bytewriter
from contextlib import contextmanager

TM_VALUE		= 0x01
TM_LIST			= 0x02

TS_RESIDENT		= 0x00
TS_GLOBAL		= 0x02
TS_CONTAIN		= 0x03

hexcodes = peridot_datatypes.hexcodes
classnames = peridot_datatypes.classnames

class peridot_pointer:
	def __init__(self):
		self.pointer_global = False
		self.pointer_filenum = -1
		self.pointer_pos = 0

	def __repr__(self):
		name_main = 'Peridot Pointer'
		endtxt = 'File:'+str(self.pointer_filenum)
		endtxt += ' Pos:'+str(self.pointer_pos)
		return '<%s - %s>' % (name_main, endtxt)

	def write(self, byw_stream):
		byw_stream.uint32(self.pointer_filenum)
		byw_stream.uint32(self.pointer_pos)

	def read(self, ebr_str):
		self.pointer_filenum = ebr_str.int_u32()
		self.pointer_pos = ebr_str.int_u32()

class peridot_typeval:
	def __init__(self):
		self.valtype = 0
		self.modifier = 0
		self.storage = 0

	def read_typeval(self, intype):
		self.valtype = intype&0xFF
		self.modifier = (intype>>8)&0xF
		self.storage = (intype>>12)&0xF
		print(self)

	def write_type(self):
		lowtype = self.valtype
		hightype = (self.modifier<<8)
		veryhightype = (self.storage<<12)
		return lowtype+hightype+veryhightype

	def __repr__(self):
		outtxt = ''
		if self.storage == TS_RESIDENT: outtxt = ''
		elif self.storage == TS_GLOBAL: outtxt = 'pointer_global:'
		elif self.storage == TS_CONTAIN: outtxt = 'pointer_local:'
		else: outtxt = 'unknown:'
		if self.modifier == TM_VALUE: outtxt += 'val:'
		elif self.modifier == TM_LIST: outtxt += 'list:'
		else: outtxt += 'unknown_%i:' % self.modifier
		if self.valtype in classnames: outtxt += classnames[self.valtype]
		else: outtxt += 'unknown'
		return '<Peridot Type - %s>' % outtxt

	def read(self, ebr_str, **kwargs):
		self.read_typeval(ebr_str.int_u16())
		return self.value_read(ebr_str, **kwargs)

	def write(self, byw_stream, value):
		byw_stream.uint16(self.write_type())
		self.value_write(byw_stream, value)

	def skip(self, ebr_str):
		self.read_typeval(ebr_str.int_u16())
		return self.value_skip(ebr_str)

	def value_write(self, byw_stream, value):
		if self.storage == TS_RESIDENT:
			if self.modifier == TM_VALUE:
				if self.valtype in hexcodes: hexcodes[self.valtype].write_single(byw_stream, value)
			elif self.modifier == TM_LIST:
				byw_stream.uint32(len(value))
				if self.valtype in hexcodes: hexcodes[self.valtype].write_list(byw_stream, value)
			else: exit('unknown write type %s' % self)
		elif self.storage == TS_GLOBAL:
			if self.modifier == TM_VALUE:
				value.write(byw_stream)
		elif self.storage == TS_CONTAIN:
			if self.modifier == TM_VALUE:
				value.write(byw_stream)

	def value_read(self, ebr_str, **kwargs):
		if self.storage == TS_RESIDENT:
			if self.modifier == TM_VALUE:
				if self.valtype in hexcodes: value = hexcodes[self.valtype].read_single(ebr_str, **kwargs)
			elif self.modifier == TM_LIST:
				count = ebr_str.int_u32()
				if self.valtype in hexcodes: value = hexcodes[self.valtype].read_list(ebr_str, count)
		elif self.storage == TS_GLOBAL:
			if self.modifier == TM_VALUE:
				value = peridot_pointer()
				value.read(ebr_str)
		elif self.storage == TS_CONTAIN:
			if self.modifier == TM_VALUE:
				value = peridot_pointer()
				value.read(ebr_str)

		return value

	def value_skip(self, ebr_str):
		if self.storage == TS_RESIDENT:
			if self.modifier == TM_VALUE:
				if self.valtype in hexcodes: 
					ebr_str.skip(hexcodes[self.valtype].skip_single(ebr_str))
			elif self.modifier == TM_LIST:
				count = ebr_str.int_u32()
				if self.valtype in hexcodes: 
					ebr_str.skip(hexcodes[self.valtype].skip_list(ebr_str, count))
		elif self.storage == TS_GLOBAL:
			if self.modifier == TM_VALUE:
				value = peridot_pointer()
				value.read(ebr_str)
				return value
		elif self.storage == TS_CONTAIN:
			if self.modifier == TM_VALUE:
				value = peridot_pointer()
				value.read(ebr_str)
				return value

	def getbytes(self, ebr_str):
		if self.storage == TS_RESIDENT:
			if self.modifier == TM_VALUE:
				if self.valtype in hexcodes: 
					skipb = hexcodes[self.valtype].skip_single(ebr_str)
					return ebr_str.raw(skipb)
			elif self.modifier == TM_LIST:
				count = ebr_str.int_u32()
				if self.valtype in hexcodes: 
					skipb = hexcodes[self.valtype].skip_list(ebr_str, count)
					return ebr_str.raw(skipb)

class peridot_part:
	def __init__(self):
		self.id = 0
		self.type = peridot_typeval()
		self.val = None
		self.is_header = False

		self.reado_loaded = False
		self.reado_pos = 0
		self.reado_load_if_needed = False

	def __repr__(self):
		return str([self.is_header, self.id, self.type, self.val if self.reado_loaded else 'Not Loaded'])

	def write(self, byw_stream):
		byw_stream.uint32(self.id+0x1000 if not self.is_header else self.id)
		self.type.write(byw_stream, self.val)

	def read(self, ebr_str):
		self.id = ebr_str.int_u32()
		self.is_header = self.id<0x1000
		if not self.is_header: self.id = self.id-0x1000
		self.reado_pos = ebr_str.tell_real()
		self.val = self.type.read(ebr_str)
		self.reado_loaded = True

	def read_notload(self, ebr_str):
		self.id = ebr_str.int_u32()
		self.is_header = self.id<0x1000
		if not self.is_header: self.id = self.id-0x1000
		self.reado_pos = ebr_str.tell_real()
		self.val = self.type.skip(ebr_str)
		if self.val is not None: self.reado_loaded = True

	def getvalue(self, ebr_str, **kwargs):
		if not self.reado_loaded:
			ebr_str.seek_real(self.reado_pos)
			self.val = self.type.read(ebr_str, **kwargs)
			self.reado_loaded = True
		return self.val

	def getbytes(self, ebr_str):
		ebr_str.seek_real(self.reado_pos+2)
		return self.type.getbytes(ebr_str)

HEADER_ID__EXTFILE_GLOBAL		= 0x00000001
HEADER_ID__EXTFILE_CONTAIN		= 0x00000002
HEADER_ID__DATATYPE				= 0x00000000

class peridot_container:
	def __init__(self):
		self.datatype = b''
		self.data = []

	def __iter__(self):
		return self.data.__iter__()

	@contextmanager
	def add_container(self, vid):
		try:
			container_obj = peridot_container()
			yield container_obj
		finally:
			part_obj = peridot_part()
			part_obj.val = container_obj.data
			part_obj.id = vid

			type_obj = part_obj.type
			type_obj.valtype = peridot_datatypes.T_CONTAINER
			type_obj.modifier = TM_VALUE
			self.data.append(part_obj)

	def add_header_value(self, vid, vtype, value):
		part_obj = peridot_part()
		part_obj.val = value
		part_obj.id = vid
		part_obj.is_header = True
		type_obj = part_obj.type
		type_obj.valtype = vtype
		type_obj.modifier = TM_VALUE
		self.data.append(part_obj)

	def add_value(self, vid, vtype, value):
		part_obj = peridot_part()
		part_obj.val = value
		part_obj.id = vid
		type_obj = part_obj.type
		type_obj.valtype = vtype
		type_obj.modifier = TM_VALUE
		self.data.append(part_obj)

	def add_value_list(self, vid, vtype, value):
		part_obj = peridot_part()
		part_obj.val = value
		part_obj.id = vid
		type_obj = part_obj.type
		type_obj.valtype = vtype
		type_obj.modifier = TM_LIST
		self.data.append(part_obj)

	def add_pointer(self, vid, vtype, filepos, filenum, isglobal):
		part_obj = peridot_part()
		part_obj.id = vid

		type_obj = part_obj.type
		type_obj.valtype = vtype
		type_obj.modifier = TM_VALUE
		type_obj.storage = TS_GLOBAL if isglobal else TS_CONTAIN

		value_obj = peridot_pointer()
		value_obj.pointer_filenum = filenum
		value_obj.pointer_pos = filepos
		part_obj.val = value_obj

		self.data.append(part_obj)

	def read_w_header(self, byw_stream, **kwargs):
		byw_stream.magic_check(b'Peridot Data Storage            ')
		self.read(byw_stream, **kwargs)

	def read(self, ebr_str, **kwargs):
		do_load = (kwargs['doload']) if 'doload' in kwargs else 1
		self.datatype = ebr_str.string(16)
		count = ebr_str.int_u32()
		headersize = ebr_str.int_u32()
		ebr_str.skip(headersize)
		for x in range(count):
			part_obj = peridot_part()
			if do_load: part_obj.read(ebr_str)
			else: part_obj.read_notload(ebr_str)
			self.data.append(part_obj)

	def read_from_file(self, filename, **kwargs):
		self.datatype = b''
		self.data = []
		ebr_str = easybinrw.binread()
		ebr_str.load_file(filename)
		self.read_w_header(ebr_str, **kwargs)
		return ebr_str

	def write_to_file(self, filename):
		byw_stream = bytewriter.bytewriter()
		self.write_w_header(byw_stream)
		f = open(filename, 'wb')
		f.write(byw_stream.getvalue())
		f.flush()
		f.close()

	def write_w_header(self, byw_stream):
		byw_stream.raw(b'Peridot Data Storage            ')
		self.write(byw_stream)

	def write(self, byw_stream):
		byw_stream.string(self.datatype, 16)
		byw_stream.uint32(len(self.data))
		byw_stream.uint32(0)
		for part_obj in self.data:
			part_obj.write(byw_stream)

	def folder_write(self):
		byw_stream = bytewriter.bytewriter()
		byw_stream.uint32(len(self.data))
		for part_obj in self.data:
			part_obj.write(byw_stream)
		return byw_stream.getvalue()

	def folder_read(self, ebr_str, **kwargs):
		do_load = (kwargs['doload']) if 'doload' in kwargs else 1
		count = ebr_str.int_u32()
		for x in range(count):
			part_obj = peridot_part()
			if do_load: part_obj.read(ebr_str)
			else: part_obj.read_notload(ebr_str)
			self.data.append(part_obj)