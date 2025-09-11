from struct import *
import mmap
import os
import numpy as np
import sys

class binread_state:
	__slots__ = ['start', 'end', 'endian']
	def __init__(self):
		self.start = 0
		self.end = 0
		self.endian = sys.byteorder=='big'

class binread:
	unp_s8 = Struct('b').unpack
	unp_u8 = Struct('B').unpack

	unp_s16_b = Struct('>h').unpack
	unp_u16_b = Struct('>H').unpack
	unp_s32_b = Struct('>i').unpack
	unp_u32_b = Struct('>L').unpack
	unp_s64_b = Struct('>q').unpack
	unp_u64_b = Struct('>Q').unpack
	unp_float_b = Struct('>f').unpack
	unp_double_b = Struct('>d').unpack

	unp_s16_l = Struct('<h').unpack
	unp_u16_l = Struct('<H').unpack
	unp_s32_l = Struct('<i').unpack
	unp_u32_l = Struct('<L').unpack
	unp_s64_l = Struct('<q').unpack
	unp_u64_l = Struct('<Q').unpack
	unp_float_l = Struct('<f').unpack
	unp_double_l = Struct('<d').unpack

	dt_s8 = np.dtype('b')
	dt_u8 = np.dtype('B')

	dt_s16_n = np.dtype('h')
	dt_u16_n = np.dtype('H')
	dt_s32_n = np.dtype('i')
	dt_u32_n = np.dtype('I')
	dt_s64_n = np.dtype('q')
	dt_u64_n = np.dtype('Q')
	dt_float_n = np.dtype('f')
	dt_double_n = np.dtype('d')

	dt_s16_b = np.dtype('>h')
	dt_u16_b = np.dtype('>H')
	dt_s32_b = np.dtype('>i')
	dt_u32_b = np.dtype('>I')
	dt_s64_b = np.dtype('>q')
	dt_u64_b = np.dtype('>Q')
	dt_float_b = np.dtype('>f')
	dt_double_b = np.dtype('>d')

	dt_s16_l = np.dtype('<h')
	dt_u16_l = np.dtype('<H')
	dt_s32_l = np.dtype('<i')
	dt_u32_l = np.dtype('<I')
	dt_s64_l = np.dtype('<q')
	dt_u64_l = np.dtype('<Q')
	dt_float_l = np.dtype('<f')
	dt_double_l = np.dtype('<d')

	def __init__(self):
		self.str = None

		self.file = None
		self.filenum = None
		self.filename = None
		self.is_file = False

		self.state = binread_state()

	def load_file(self, filename):
		try:
			self.state.__init__()

			self.file = open(filename, 'rb')
			self.filenum = self.file.fileno()
			self.filename = filename
			self.is_file = True

			self.str = mmap.mmap(self.filenum, 0, access=mmap.ACCESS_READ)
			self.state.end = os.path.getsize(filename)
			return True
		except:
			self.__init__()
			return False

	def fileno(self): return self.filenum

	def magic_check(self, bind): assert bind==self.str.read(len(bind))

	def read(self, num): return self.str.read(num)
	def tell(self): return self.str.tell()

	def read_real(self, num): return self.str.read(num)
	def tell_real(self): return self.str.tell()-self.state.start

	def seek(self, num): return self.str.seek(num+self.state.start)
	def seek_real(self, num): return self.str.seek(num+self.state.start)

	def skip(self, num): return self.str.seek(self.str.tell()+num)

	def remaining(self): return max(0, self.state.end-self.tell())
	def rest(self): return self.str.read(self.remaining())

	def int_s8(self): return self.unp_s8(self.str.read(1))[0]
	def int_u8(self): return self.unp_u8(self.str.read(1))[0]

	def int_s16(self): return (self.unp_s16_b if self.state.endian else self.unp_s16_l)(self.str.read(2))[0] 
	def int_u16(self): return (self.unp_u16_b if self.state.endian else self.unp_u16_l)(self.str.read(2))[0] 
	def int_s32(self): return (self.unp_s32_b if self.state.endian else self.unp_s32_l)(self.str.read(4))[0] 
	def int_u32(self): return (self.unp_u32_b if self.state.endian else self.unp_u32_l)(self.str.read(4))[0] 
	def int_s64(self): return (self.unp_s64_b if self.state.endian else self.unp_s64_l)(self.str.read(8))[0] 
	def int_u64(self): return (self.unp_u64_b if self.state.endian else self.unp_u64_l)(self.str.read(8))[0] 
	def float(self): return (self.unp_float_b if self.state.endian else self.unp_float_l)(self.str.read(4))[0] 
	def double(self): return (self.unp_double_b if self.state.endian else self.unp_double_l)(self.str.read(8))[0] 

	def int_s16_b(self): return self.unp_s16_b(self.str.read(2))[0]
	def int_u16_b(self): return self.unp_u16_b(self.str.read(2))[0]
	def int_s32_b(self): return self.unp_s32_b(self.str.read(4))[0]
	def int_u32_b(self): return self.unp_u32_b(self.str.read(4))[0]
	def int_s64_b(self): return self.unp_s64_b(self.str.read(8))[0]
	def int_u64_b(self): return self.unp_u64_b(self.str.read(8))[0]
	def float_b(self): return self.unp_float_b(self.str.read(4))[0]
	def double_b(self): return self.unp_double_b(self.str.read(8))[0]

	def int_s16_l(self): return self.unp_s16_l(self.str.read(2))[0]
	def int_u16_l(self): return self.unp_u16_l(self.str.read(2))[0]
	def int_s32_l(self): return self.unp_s32_l(self.str.read(4))[0]
	def int_u32_l(self): return self.unp_u32_l(self.str.read(4))[0]
	def int_s64_l(self): return self.unp_s64_l(self.str.read(8))[0]
	def int_u64_l(self): return self.unp_u64_l(self.str.read(8))[0]
	def float_l(self): return self.unp_float_l(self.str.read(4))[0]
	def double_l(self): return self.unp_double_l(self.str.read(8))[0]

	def raw(self, num): return self.str.read(num)
	def string(self, num, **k): return self.str.read(num).decode(**k)

	def internal_readarr(self, num, numbytes, dtype): 
		byteds = self.read(num*numbytes)
		return np.frombuffer(byteds, dtype)

	def list_int_s8(self, num): return self.internal_readarr(num, 1, self.dt_s8)
	def list_int_u8(self, num): return self.internal_readarr(num, 1, self.dt_u8)

	def list_int_s16(self, num): return self.internal_readarr(num, 2, self.dt_s16_b if self.state.endian else self.dt_s16_l)
	def list_int_u16(self, num): return self.internal_readarr(num, 2, self.dt_u16_b if self.state.endian else self.dt_u16_l)
	def list_int_s32(self, num): return self.internal_readarr(num, 4, self.dt_s32_b if self.state.endian else self.dt_s32_l)
	def list_int_u32(self, num): return self.internal_readarr(num, 4, self.dt_u32_b if self.state.endian else self.dt_u32_l)
	def list_int_s64(self, num): return self.internal_readarr(num, 8, self.dt_s64_b if self.state.endian else self.dt_s64_l)
	def list_int_u64(self, num): return self.internal_readarr(num, 8, self.dt_u64_b if self.state.endian else self.dt_u64_l)
	def list_float(self, num): return self.internal_readarr(num, 4, self.dt_float_b if self.state.endian else self.dt_float_l)
	def list_double(self, num): return self.internal_readarr(num, 8, self.dt_double_b if self.state.endian else self.dt_double_l)

	def list_int_s16_b(self, num): return self.internal_readarr(num, 2, self.dt_s16_b)
	def list_int_u16_b(self, num): return self.internal_readarr(num, 2, self.dt_u16_b)
	def list_int_s32_b(self, num): return self.internal_readarr(num, 4, self.dt_s32_b)
	def list_int_u32_b(self, num): return self.internal_readarr(num, 4, self.dt_u32_b)
	def list_int_s64_b(self, num): return self.internal_readarr(num, 8, self.dt_s64_b)
	def list_int_u64_b(self, num): return self.internal_readarr(num, 8, self.dt_u64_b)
	def list_float_b(self, num): return self.internal_readarr(num, 4, self.dt_float_b)
	def list_double_b(self, num): return self.internal_readarr(num, 8, self.dt_double_b)

	def list_int_s16_l(self, num): return self.internal_readarr(num, 2, self.dt_s16_l)
	def list_int_u16_l(self, num): return self.internal_readarr(num, 2, self.dt_u16_l)
	def list_int_s32_l(self, num): return self.internal_readarr(num, 4, self.dt_s32_l)
	def list_int_u32_l(self, num): return self.internal_readarr(num, 4, self.dt_u32_l)
	def list_int_s64_l(self, num): return self.internal_readarr(num, 8, self.dt_s64_l)
	def list_int_u64_l(self, num): return self.internal_readarr(num, 8, self.dt_u64_l)
	def list_float_l(self, num): return self.internal_readarr(num, 4, self.dt_float_l)
	def list_double_l(self, num): return self.internal_readarr(num, 8, self.dt_double_l)