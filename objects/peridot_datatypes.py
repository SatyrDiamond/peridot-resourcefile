from objects import easybinrw
from objects.data_bytes import bytewriter
from contextlib import contextmanager

T_NONE			= 0x00
T_UINT8			= 0x01
T_UINT16		= 0x02
T_UINT32		= 0x03
T_UINT64		= 0x04
T_INT8			= 0x05
T_INT16			= 0x06
T_INT32			= 0x07
T_INT64			= 0x08
T_BOOL			= 0x09
T_FLOAT			= 0x0A
T_DOUBLE		= 0x0B
T_STRING		= 0x0C
T_BYTES			= 0x0D
T_LONGSTRING	= 0x10

T_CONTAINER		= 0xFF

class classval_none:
	name = 'none'
	hexcode = T_NONE
	def write_single(byw_stream, value): pass
	def write_list(byw_stream, value): pass
	def read_single(ebr_str, **kwargs): return None
	def read_list(ebr_str, count): return None
	def skip_single(ebr_str): return 0
	def skip_list(ebr_str, count): return 0
class classval_uint8:
	name = 'uint8'
	hexcode = T_UINT8
	def write_single(byw_stream, value): byw_stream.uint8(value)
	def write_list(byw_stream, value): byw_stream.l_uint8(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_u8()
	def read_list(ebr_str, count): return ebr_str.list_int_u8(count)
	def skip_single(ebr_str): return 1
	def skip_list(ebr_str, count): return count
class classval_uint16:
	name = 'uint16'
	hexcode = T_UINT16
	def write_single(byw_stream, value): byw_stream.uint16(value)
	def write_list(byw_stream, value): byw_stream.l_uint16(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_u16()
	def read_list(ebr_str, count): return ebr_str.list_int_u16(count)
	def skip_single(ebr_str): return 2
	def skip_list(ebr_str, count): return count*2
class classval_uint32:
	name = 'uint32'
	hexcode = T_UINT32
	def write_single(byw_stream, value): byw_stream.uint32(value)
	def write_list(byw_stream, value): byw_stream.l_uint32(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_u32()
	def read_list(ebr_str, count): return ebr_str.list_int_u32(count)
	def skip_single(ebr_str): return 4
	def skip_list(ebr_str, count): return count*4
class classval_uint64:
	name = 'uint64'
	hexcode = T_UINT64
	def write_single(byw_stream, value): byw_stream.uint64(value)
	def write_list(byw_stream, value): 
		for x in value: byw_stream.uint64(x)
	def read_single(ebr_str, **kwargs): return ebr_str.int_u64()
	def read_list(ebr_str, count): return [ebr_str.int_u64() for x in range(count)]
	def skip_single(ebr_str): return 8
	def skip_list(ebr_str, count): return count*8
class classval_int8:
	name = 'int8'
	hexcode = T_INT8
	def write_single(byw_stream, value): byw_stream.int8(value)
	def write_list(byw_stream, value): byw_stream.l_int8(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int8()
	def read_list(ebr_str, count): return ebr_str.list_int_s8(count)
	def skip_single(ebr_str): return 1
	def skip_list(ebr_str, count): return count
class classval_int16:
	name = 'int16'
	hexcode = T_INT16
	def write_single(byw_stream, value): byw_stream.int16(value)
	def write_list(byw_stream, value): byw_stream.l_uint16(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int_s16()
	def read_list(ebr_str, count): return ebr_str.list_int_s16(count)
	def skip_single(ebr_str): return 2
	def skip_list(ebr_str, count): return count*2
class classval_int32:
	name = 'int32'
	hexcode = T_INT32
	def write_single(byw_stream, value): byw_stream.int32(value)
	def write_list(byw_stream, value): byw_stream.l_int32(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.int32()
	def read_list(ebr_str, count): return ebr_str.list_int_s32(count)
	def skip_single(ebr_str): return 4
	def skip_list(ebr_str, count): return count*4
class classval_int64:
	name = 'int64'
	hexcode = T_INT64
	def write_single(byw_stream, value): byw_stream.int64(value)
	def write_list(byw_stream, value): 
		for x in value: byw_stream.int64(x)
	def read_single(ebr_str, **kwargs): return ebr_str.int64()
	def read_list(ebr_str, count): return [ebr_str.list_int_s64() for x in range(count)]
	def skip_single(ebr_str): return 8
	def skip_list(ebr_str, count): return count*8
class classval_bool:
	name = 'bool'
	hexcode = T_BOOL
	def write_single(byw_stream, value): byw_stream.int8(int(value))
	def write_list(byw_stream, value): byw_stream.l_int8(value, len(value))
	def read_single(ebr_str, **kwargs): return bool(ebr_str.int8())
	def read_list(ebr_str, count): return ebr_str.list_int_s8(count)
	def skip_single(ebr_str): return 1
	def skip_list(ebr_str, count): return count*1
class classval_float:
	name = 'float'
	hexcode = T_FLOAT
	def write_single(byw_stream, value): byw_stream.float(value)
	def write_list(byw_stream, value): byw_stream.l_float(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.float()
	def read_list(ebr_str, count): return ebr_str.list_float(count)
	def skip_single(ebr_str): return 4
	def skip_list(ebr_str, count): return count*4
class classval_double:
	name = 'double'
	hexcode = T_DOUBLE
	def write_single(byw_stream, value): byw_stream.double(value)
	def write_list(byw_stream, value): byw_stream.l_double(value, len(value))
	def read_single(ebr_str, **kwargs): return ebr_str.double()
	def read_list(ebr_str, count): return ebr_str.list_double(count)
	def skip_single(ebr_str): return 8
	def skip_list(ebr_str, count): return count*8
class classval_string:
	name = 'string'
	hexcode = T_STRING
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
	hexcode = T_BYTES
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
	hexcode = T_CONTAINER
	def write_single(byw_stream, value): 
		from objects.peridot_obj import peridot_container
		c = peridot_container()
		c.datatype = b'Folder'
		c.data = value
		byw_stream.c_raw__int32(c.folder_write(), True)
	def read_single(ebr_str, **kwargs): 
		from objects.peridot_obj import peridot_container
		datasize = ebr_str.int_u32()
		value = peridot_container()
		value.datatype = b'Folder'
		value.folder_read(ebr_str, **kwargs)
		return value.data
	def skip_single(ebr_str): return ebr_str.int_u32()
class classval_longstring:
	name = 'longstring'
	hexcode = T_LONGSTRING
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
