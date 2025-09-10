from objects import easybinrw
from objects.data_bytes import bytewriter
from contextlib import contextmanager

T_NONE			= 0x0000
T_UINT8			= 0x0001
T_UINT16		= 0x0002
T_UINT32		= 0x0003
T_UINT64		= 0x0004
T_INT8			= 0x0005
T_INT16			= 0x0006
T_INT32			= 0x0007
T_INT64			= 0x0008
T_BOOL			= 0x0009
T_FLOAT			= 0x000A
T_DOUBLE		= 0x000B
T_STRING		= 0x000C
T_BYTES			= 0x000D
T_CONTAINER		= 0xFFFF
T_LONGSTRING	= 0x0010

TM_VALUE		= 0x01
TM_LIST			= 0x02

TS_RESIDENT		= 0x00
TS_GLOBAL		= 0x01
TS_CONTAIN		= 0x02

class classval_none:
	name = 'none'
	hexcode = 0x0000
	def write_single(byw_stream, value): pass
	def write_list(byw_stream, value): pass
	def read_single(ebr_str, **kwargs): return None
	def read_list(ebr_str, count): return None
class classval_uint8:
	name = 'uint8'
	hexcode = 0x0001
	def write_single(byw_stream, value): byw_stream.uint8(value)
	def write_list(byw_stream, value): byw_stream.l_uint8(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_u8()
	def read_list(ebr_str, count): return ebr_str.list_int_u8(count)
	def skip_single(ebr_str): return 1
	def skip_list(ebr_str, count): return count
class classval_uint16:
	name = 'uint16'
	hexcode = 0x0002
	def write_single(byw_stream, value): byw_stream.uint16(value)
	def write_list(byw_stream, value): byw_stream.l_uint16(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_u16()
	def read_list(ebr_str, count): return ebr_str.list_int_u16(count)
	def skip_single(ebr_str): return 2
	def skip_list(ebr_str, count): return count*2
class classval_uint32:
	name = 'uint32'
	hexcode = 0x0003
	def write_single(byw_stream, value): byw_stream.uint32(value)
	def write_list(byw_stream, value): byw_stream.l_uint32(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_u32()
	def read_list(ebr_str, count): return ebr_str.list_int_u32(count)
	def skip_single(ebr_str): return 4
	def skip_list(ebr_str, count): return count*4
class classval_uint64:
	name = 'uint64'
	hexcode = 0x0004
	def write_single(byw_stream, value): byw_stream.uint64(value)
	def write_list(byw_stream, value): 
		for x in value: byw_stream.uint64(x)
	def read_single(ebr_str, **kwargs): return ebr_str.int_u64()
	def read_list(ebr_str, count): return [ebr_str.int_u64() for x in range(count)]
	def skip_single(ebr_str): return 8
	def skip_list(ebr_str, count): return count*8
class classval_int8:
	name = 'int8'
	hexcode = 0x0005
	def write_single(byw_stream, value): byw_stream.int8(value)
	def write_list(byw_stream, value): byw_stream.l_int8(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int8()
	def read_list(ebr_str, count): return ebr_str.list_int_s8(count)
	def skip_single(ebr_str): return 1
	def skip_list(ebr_str, count): return count
class classval_int16:
	name = 'int16'
	hexcode = 0x0006
	def write_single(byw_stream, value): byw_stream.int16(value)
	def write_list(byw_stream, value): byw_stream.l_uint16(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_s16()
	def read_list(ebr_str, count): return ebr_str.list_int_s16(count)
	def skip_single(ebr_str): return 2
	def skip_list(ebr_str, count): return count*2
class classval_int32:
	name = 'int32'
	hexcode = 0x0007
	def write_single(byw_stream, value): byw_stream.int32(value)
	def write_list(byw_stream, value): byw_stream.l_int32(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int32()
	def read_list(ebr_str, count): return ebr_str.list_int_s32(count)
	def skip_single(ebr_str): return 4
	def skip_list(ebr_str, count): return count*4
class classval_int64:
	name = 'int64'
	hexcode = 0x0008
	def write_single(byw_stream, value): byw_stream.int64(value)
	def write_list(byw_stream, value): 
		for x in value: byw_stream.int64(x)
	def read_single(ebr_str, **kwargs): return ebr_str.int64()
	def read_list(ebr_str, count): return [ebr_str.list_int_s64() for x in range(count)]
	def skip_single(ebr_str): return 8
	def skip_list(ebr_str, count): return count*8
class classval_bool:
	name = 'bool'
	hexcode = 0x0009
	def write_single(byw_stream, value): byw_stream.int8(int(value))
	def write_list(byw_stream, value): byw_stream.l_int8(value, len(value))
	def read_single(ebr_str, **kwargs): return bool(ebr_str.int8())
	def read_list(ebr_str, count): return ebr_str.list_int_s8(count)
	def skip_single(ebr_str): return 1
	def skip_list(ebr_str, count): return count*1
class classval_float:
	name = 'float'
	hexcode = 0x000A
	def write_single(byw_stream, value): byw_stream.float(value)
	def write_list(byw_stream, value): byw_stream.l_float(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.float()
	def read_list(ebr_str, count): return ebr_str.list_float(count)
	def skip_single(ebr_str): return 4
	def skip_list(ebr_str, count): return count*4
class classval_double:
	name = 'double'
	hexcode = 0x000B
	def write_single(byw_stream, value): byw_stream.double(value)
	def write_list(byw_stream, value): byw_stream.l_double(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.double()
	def read_list(ebr_str, count): return ebr_str.list_double(count)
	def skip_single(ebr_str): return 8
	def skip_list(ebr_str, count): return count*8
class classval_string:
	name = 'string'
	hexcode = 0x000C
	def write_single(byw_stream, value): byw_stream.c_raw__int8(value.encode())
	def write_list(byw_stream, value): 
		ibyw_stream = bytewriter.bytewriter()
		for x in value: ibyw_stream.c_raw__int8(x.encode())
		outval = ibyw_stream.getvalue()
		byw_stream.uint32(len(outval))
		byw_stream.raw(ibyw_stream.getvalue())
	def read_single(ebr_str, **kwargs): return ebr_str.string(ebr_str.int_u8())
	def read_list(ebr_str, count): ebr_str.skip(ebr_str.int_u32())
	def skip_single(ebr_str): return ebr_str.int_u8()
	def skip_list(ebr_str, count): return ebr_str.int_u32()
class classval_raw:
	name = 'raw'
	hexcode = 0x000D
	def write_single(byw_stream, value): byw_stream.c_raw__int32(value, True)
	def write_list(byw_stream, value): 
		ibyw_stream = bytewriter.bytewriter()
		for x in value: ibyw_stream.c_raw__int32(x, True)
		outval = ibyw_stream.getvalue()
		byw_stream.uint32(len(outval))
		byw_stream.raw(ibyw_stream.getvalue())
	def read_single(ebr_str, **kwargs): return ebr_str.raw(ebr_str.int_u32())
	def read_list(ebr_str, count): 
		endpos = ebr_str.tell_real()+ebr_str.int_u32()+4
		outval = [ebr_str.raw(ebr_str.int_u32()) for x in range(count)]
		ebr_str.seek_real(endpos)
		return outval
	def skip_single(ebr_str): return ebr_str.int_u32()
	def skip_list(ebr_str, count): return ebr_str.int_u32()
class classval_container:
	name = 'container'
	hexcode = 0xFFFF
	def write_single(byw_stream, value): 
		c = peridot_container()
		c.datatype = b'Folder'
		c.data = value
		byw_stream.c_raw__int32(c.folder_write(), True)
	def read_single(ebr_str, **kwargs): 
		datasize = ebr_str.int_u32()
		value = peridot_container()
		value.datatype = b'Folder'
		value.folder_read(ebr_str, **kwargs)
		return value.data
	def skip_single(ebr_str): return ebr_str.int_u32()
class classval_longstring:
	name = 'longstring'
	hexcode = 0x0010
	def write_single(byw_stream, value): byw_stream.c_raw__int32(value.encode(), True)
	def write_list(byw_stream, value): 
		ibyw_stream = bytewriter.bytewriter()
		for x in value: ibyw_stream.c_raw__int32(x.encode(), True)
		outval = ibyw_stream.getvalue()
		byw_stream.uint32(len(outval))
		byw_stream.raw(ibyw_stream.getvalue())
	def read_single(ebr_str, **kwargs): return ebr_str.string(ebr_str.int_u32())
	def read_list(ebr_str, count): 
		endpos = ebr_str.tell_real()+ebr_str.int_u32()+4
		outval = [ebr_str.string(ebr_str.int_u32()) for x in range(count)]
		ebr_str.seek_real(endpos)
		return outval
	def skip_single(ebr_str): return ebr_str.int_u32()
	def skip_list(ebr_str, count): return ebr_str.int_u32()

inclass = [
classval_none,
classval_uint8,
classval_uint16,
classval_uint32,
classval_uint64,
classval_int8,
classval_int16,
classval_int32,
classval_int64,
classval_bool,
classval_float,
classval_double,
classval_string,
classval_raw,
classval_container,
classval_longstring,
]

hexcodes = dict([[x.hexcode, x] for x in inclass])
classnames = dict([[x.hexcode, x.name] for x in inclass])

class peridot_pointer:
	def __init__(self):
		self.pointer_global = False
		self.pointer_filenum = 0
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
		self.valtype = intype&0xFFFF
		self.modifier = (intype>>16)&0xFF
		self.storage = (intype>>24)&0xFF

	def write_type(self):
		lowtype = self.valtype
		hightype = (self.modifier<<16)
		veryhightype = (self.storage<<24)
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
		self.read_typeval(ebr_str.int_u32())
		return self.value_read(ebr_str, **kwargs)

	def write(self, byw_stream, value):
		byw_stream.uint32(self.write_type())
		self.value_write(byw_stream, value)

	def skip(self, ebr_str):
		self.read_typeval(ebr_str.int_u32())
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
		ebr_str.seek_real(self.reado_pos+4)
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
			type_obj.valtype = T_CONTAINER
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