import struct
import varint
import os
import numpy as np
import mmap
from io import BytesIO
from contextlib import contextmanager

class bytereader:
	unpack_byte = struct.Struct('B').unpack
	unpack_s_byte = struct.Struct('b').unpack

	unpack_short = struct.Struct('<H').unpack
	unpack_short_b = struct.Struct('>H').unpack
	unpack_s_short = struct.Struct('<h').unpack
	unpack_s_short_b = struct.Struct('>h').unpack
	
	unpack_int = struct.Struct('<I').unpack
	unpack_int_b = struct.Struct('>I').unpack
	unpack_s_int = struct.Struct('<i').unpack
	unpack_s_int_b = struct.Struct('>i').unpack
	
	unpack_float = struct.Struct('<f').unpack
	unpack_float_b = struct.Struct('>f').unpack
	unpack_double = struct.Struct('<d').unpack
	unpack_double_b = struct.Struct('>d').unpack

	unpack_long = struct.Struct('<Q').unpack
	unpack_long_b = struct.Struct('>Q').unpack
	unpack_s_long = struct.Struct('<q').unpack
	unpack_s_long_b = struct.Struct('>q').unpack
	
	def __init__(self, *argv):
		self.buf = None
		self.start = 0
		self.end = 0
		self.iso_range = []
		if argv:
			self.load_raw(argv[0])

	def load_file(self, filename):
		if os.path.exists(filename):
			file_stats = os.stat(filename)
			self.end = file_stats.st_size
			f = open(filename)
			self.buf = mmap.mmap(f.fileno(), 0, access = mmap.ACCESS_READ)
			return True
		else:
			#print('File Not Found', filename)
			return False

	def load_raw(self, rawdata):
		self.end = len(rawdata)
		self.buf = BytesIO(rawdata)

	def magic_check(self, headerbytes):
		if self.buf.read(len(headerbytes)) == headerbytes: return True
		else: raise ValueError('Magic Check Failed: '+str(headerbytes))

	def read(self, num): return self.buf.read(num)

	def tell(self): return self.buf.tell()-self.start

	def seek(self, num): return self.buf.seek(num+self.start)

	def skip(self, num): return self.buf.seek(self.tell()+num+self.start)

	def tell_real(self): return self.buf.tell()

	def seek_real(self, num): return self.buf.seek(num)

	def skip_real(self, num): return self.buf.seek(self.tell()+num)

	@contextmanager
	def isolate_range(self, start, end, set_end):
		try:
			#print('ENTER', self.start, self.end, self.end-self.start, '>', start, end, end-start, self.iso_range)
			self.iso_range.append([self.start, self.end, self.tell_real()])
			self.start = start
			self.end = end
			self.seek(0)
			yield self
		finally:
			real_start, real_end, real_pos = self.iso_range[-1]
			self.iso_range = self.iso_range[:-1]
			self.start = real_start
			self.end = real_end
			self.seek_real(end if set_end else real_pos)
			#print('EXIT', self.start, self.end, self.end-self.start, '>', real_start, real_end, real_end-real_start, self.iso_range)

	def isolate_size(self, size, set_end):
		start = self.tell_real()
		return self.isolate_range(start, start+size, set_end)

	def remaining(self): return max(0, self.end - self.buf.tell())

	def uint8(self): return self.unpack_byte(self.buf.read(1))[0]
	def int8(self): return self.unpack_s_byte(self.buf.read(1))[0]

	def uint16(self): return self.unpack_short(self.buf.read(2))[0]
	def uint16_b(self): return self.unpack_short_b(self.buf.read(2))[0]
	def int16(self): return self.unpack_s_short(self.buf.read(2))[0]
	def int16_b(self): return self.unpack_s_short_b(self.buf.read(2))[0]

	def uint24(self): return self.unpack_int(self.buf.read(3)+b'\x00')[0]
	def uint24_b(self): return self.unpack_int_b(b'\x00'+self.buf.read(3))[0]

	def uint32(self): return self.unpack_int(self.buf.read(4))[0]
	def uint32_b(self): return self.unpack_int_b(self.buf.read(4))[0]
	def int32(self): return self.unpack_s_int(self.buf.read(4))[0]
	def int32_b(self): return self.unpack_s_int_b(self.buf.read(4))[0]

	def uint64(self): return self.unpack_long(self.buf.read(8))[0]
	def uint64_b(self): return self.unpack_long_b(self.buf.read(8))[0]
	def int64(self): return self.unpack_s_long(self.buf.read(8))[0]
	def int64_b(self): return self.unpack_s_long_b(self.buf.read(8))[0]

	def float(self): return self.unpack_float(self.buf.read(4))[0]
	def float_b(self): return self.unpack_float_b(self.buf.read(4))[0]

	def double(self): return self.unpack_double(self.buf.read(8))[0]
	def double_b(self): return self.unpack_double_b(self.buf.read(8))[0]

	def varint(self): return varint.decode_stream(self.buf)

	def raw(self, size): return self.buf.read(size)

	def debug_peek(self): 
		self.buf.seek(self.buf.tell()-64)
		print(self.buf.read(128)) 

	def rest(self): return self.buf.read(self.end-self.buf.tell())

	def string(self, size, **kwargs): 
		return self.buf.read(size).split(b'\x00')[0].decode(**kwargs)
	def string16(self, size): 
		return self.buf.read(size*2).decode("utf-16").rstrip('\x00')

	def l_uint8(self, num): return np.frombuffer(self.buf.read(num), dtype=np.uint8)
	def l_int8(self, num): return np.frombuffer(self.buf.read(num), dtype=np.int8)

	def l_uint16(self, num): return [self.uint16() for _ in range(num)]
	def l_uint16_b(self, num): return [self.uint16_b() for _ in range(num)]
	def l_int16(self, num): return [self.int16() for _ in range(num)]
	def l_int16_b(self, num): return [self.int16_b() for _ in range(num)]

	def l_uint32(self, num): return [self.uint32() for _ in range(num)]
	def l_uint32_b(self, num): return [self.uint32_b() for _ in range(num)]
	def l_int32(self, num): return [self.int32() for _ in range(num)]
	def l_int32_b(self, num): return [self.int32_b() for _ in range(num)]

	def l_float(self, num): return [self.float() for _ in range(num)]
	def l_float_b(self, num): return [self.float_b() for _ in range(num)]

	def l_double(self, num): return [self.double() for _ in range(num)]
	def l_double_b(self, num): return [self.double_b() for _ in range(num)]

	def l_string(self, num, size): return [self.string(size) for _ in range(num)]
