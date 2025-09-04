from objects.peridot_obj import *
from functions.values_datatype import *
from objects.data_bytes import bytewriter
from objects.data_bytes import bytereader
from functions import compression

from PIL import Image
import os
import io
import numpy as np
import varint

import qoi
import zlib
import brotli
import lzma
import bz2
import fastlz

ID_COLOR = 1
ID_SIZE = 2
ID_DATA = 3
ID_COMPRESSTYPE = 4
ID_PALLETE_COLORTYPE = 5
ID_PALLETE_DATA = 6

ID_EDITOR_FILENAME = 100
ID_EDITOR_FILETYPE = 101
ID_EDITOR_FILEPATH = 102
ID_EDITOR_ORG_COLORTYPE = 103

COL_TYPE_GRAY_1 = 'BW_1'
COL_TYPE_GRAY_8 = 'BW_8'
COL_TYPE_GRAY_8A = 'BW_8A'
COL_TYPE_GRAY_16 = 'BW_16'
COL_TYPE_RGB_8 = 'RGB_8'
COL_TYPE_RGBA_8 = 'RGBA_8'
COL_TYPE_INDEX_8 = 'IDX_8'

COL_TYPE_INDEX_1 = 'IDX_1'
COL_TYPE_INDEX_4 = 'IDX_4'
COL_TYPE_INDEXA_4 = 'IDX_4A'
COL_TYPE_INDEXA_8 = 'IDX_8A'
COL_TYPE_INDEXSA_8 = 'IDX_8A_SEP'
COL_TYPE_WHITE_8A = 'WHITE_8A'
COL_TYPE_BLACK_8A = 'BLACK_8A'
COL_TYPE_GRAY_INDEX_4 = 'IDX_BW_4'

VERBOSE_COLTYPECHANGE = False
MAX_MEGAPIXEL_SMALLER = 3000000

def compress_qoi(image_mode, rawdata, width, height): 
	if image_mode == COL_TYPE_RGB_8:
		rgb = np.frombuffer(rawdata, 'B')
		rgb = rgb.reshape((width, height, 3))
		rawdata = qoi.encode(rgb)
		return rawdata
	elif image_mode == COL_TYPE_RGBA_8:
		rgb = np.frombuffer(rawdata, 'B')
		rgb = rgb.reshape((width, height, 4))
		rawdata = qoi.encode(rgb)
		return rawdata

sir16_8_compat = [
	COL_TYPE_GRAY_8, 
	COL_TYPE_INDEXA_8, 
	COL_TYPE_INDEX_8, 
	COL_TYPE_WHITE_8A, 
	COL_TYPE_BLACK_8A,
	COL_TYPE_GRAY_1,
	COL_TYPE_INDEX_1,
	]

sir16a_8_compat = [
	COL_TYPE_GRAY_8A, 
	COL_TYPE_INDEXSA_8, 
	]

sir8_4_compat = [
	COL_TYPE_INDEX_4,
	COL_TYPE_INDEXA_4,
	COL_TYPE_GRAY_INDEX_4, 
	COL_TYPE_GRAY_1,
	COL_TYPE_INDEX_1,
	]

def compress_sir16(image_mode, rawdata): 
	if image_mode in sir16_8_compat:
		return compression.compress_sir16_256(rawdata)
	if image_mode in sir8_4_compat:
		return compression.compress_sir16_16(rawdata)
	if image_mode in sir16a_8_compat:
		return compression.compress_sir16a_256(rawdata)

def compress_sir8(image_mode, rawdata): 
	if image_mode in sir8_4_compat:
		return compression.compress_sir8(rawdata)

def decompress_sir16(image_mode, rawdata): 
	if image_mode in sir16_8_compat:
		return compression.decompress_sir16_256(rawdata)
	if image_mode in sir8_4_compat:
		return compression.decompress_sir16_16(rawdata)
	if image_mode in sir16a_8_compat:
		return compression.decompress_sir16a_256(rawdata)

def decompress_sir8(image_mode, rawdata): 
	if image_mode in sir8_4_compat:
		return compression.decompress_sir8(rawdata)

class peridot_image:
	def __init__(self):
		self.width = 1
		self.height = 1
		self.compress_li_mode = None
		self.compress_mode = None
		self.pal_ctype = COL_TYPE_RGB_8
		self.pal_data = []
		self.img_ctype = COL_TYPE_RGB_8
		self.img_data = b'\0\0\0'
		self.img_org_ctype = None

	def is_compressed(self):
		return (self.compress_mode or self.compress_li_mode)

	def get_comptxt(self):
		o = str(self.compress_li_mode)+(':' if self.compress_mode else '') if self.compress_li_mode else ''
		if self.compress_mode: o += self.compress_mode
		return o if o else None

	def compress(self, comptype):
		if not (self.compress_mode):
			if 'zlib' == comptype: orawdata = zlib.compress(self.img_data, 1)
			elif 'lzma' == comptype: orawdata = compress_lzma(self.img_data)
			elif 'brotli' == comptype: orawdata = brotli.compress(self.img_data)
			elif 'bz2' == comptype: orawdata = bz2.compress(self.img_data)
			elif 'lz77' == comptype: orawdata = fastlz.compress(self.img_data)
			if orawdata is not None:
				if len(orawdata)<len(self.img_data):
					self.img_data = orawdata
					self.compress_mode = comptype
					return True

	def li_compress(self, li_comptype, comptype):
		if not (self.compress_mode or self.compress_li_mode):
			orawdata = self.img_data
			if li_comptype == 'qoi': orawdata = compress_qoi(self.img_ctype, orawdata, self.width, self.height)
			if li_comptype == 'sir8': orawdata = compress_sir8(self.img_ctype, orawdata)
			if li_comptype == 'sir16': orawdata = compress_sir16(self.img_ctype, orawdata)
			if orawdata:
				if 'zlib' == comptype: orawdata = zlib.compress(orawdata, 1)
				elif 'lzma' == comptype: orawdata = compress_lzma(orawdata)
				elif 'brotli' == comptype: orawdata = brotli.compress(orawdata)
		
				if len(orawdata)<len(self.img_data):
					self.img_data = orawdata
					self.compress_li_mode = li_comptype
					self.compress_mode = comptype
					return True

	def compress_veryfast(self):
		if not self.compress_mode:
			rawdata = self.img_data
			bestsizelist = []
			bestsizelist.append([None, None, rawdata])

			if self.img_ctype in [COL_TYPE_RGB_8, COL_TYPE_RGBA_8]:
				bestsizelist.append(['qoi', None, 
					compress_qoi(self.img_ctype, rawdata, self.width, self.height)
					])
	
			bestsizelist.append([None, 'lz77', fastlz.compress(rawdata)])

			rle_data = compress_sir8(self.img_ctype, rawdata)
			if rle_data: 
				bestsizelist.append(['sir8', None, rle_data])
			#	bestsizelist.append(['sir8', 'lz77', fastlz.compress(rle_data)])

			rle_data = compress_sir16(self.img_ctype, rawdata)
			if rle_data: 
				bestsizelist.append(['sir16', None, rle_data])
			#	bestsizelist.append(['sir16', 'lz77', fastlz.compress(rle_data)])

			bestsizelist = dict([[len(x[2]), x] for x in bestsizelist])
			self.compress_li_mode, self.compress_mode, self.img_data = bestsizelist[sorted(bestsizelist)[0]]
			return self.compress_li_mode or self.compress_mode

	def compress_fast(self):
		if not self.compress_mode:
			rawdata = self.img_data
			bestsizelist = []
			bestsizelist.append([None, None, rawdata])
			bestsizelist.append([None, 'lz77', fastlz.compress(rawdata)])
			bestsizelist.append([None, 'lzma', compress_lzma(rawdata)])
			
			if self.img_ctype == COL_TYPE_RGB_8 or self.img_ctype == COL_TYPE_RGBA_8:
				qoid = compress_qoi(self.img_ctype, rawdata, self.width, self.height)
				bestsizelist.append(['qoi', 'lz77', fastlz.compress(qoid)])
				bestsizelist.append(['qoi', 'lzma', compress_lzma(qoid)])

			rle_data = compress_sir8(self.img_ctype, rawdata)
			if rle_data: 
				bestsizelist.append(['sir8', None, rle_data])
				bestsizelist.append(['sir8', 'lz77', fastlz.compress(rle_data)])
				bestsizelist.append(['sir8', 'lzma', compress_lzma(rle_data)])

			rle_data = compress_sir16(self.img_ctype, rawdata)
			if rle_data: 
				bestsizelist.append(['sir16', None, rle_data])
				bestsizelist.append(['sir16', 'lz77', fastlz.compress(rle_data)])
				bestsizelist.append(['sir16', 'lzma', compress_lzma(rle_data)])

			bestsizelist = dict([[len(x[2]), x] for x in bestsizelist])
			self.compress_li_mode, self.compress_mode, self.img_data = bestsizelist[sorted(bestsizelist)[0]]
			return self.compress_li_mode or self.compress_mode

	def compress_best(self):
		if not self.compress_mode:
			rawdata = self.img_data
			bestsizelist = []
			bestsizelist.append([None, None, rawdata])
			bestsizelist.append([None, 'zlib', zlib.compress(rawdata, 1)])
			bestsizelist.append([None, 'lzma', compress_lzma(rawdata)])
			bestsizelist.append([None, 'brotli', brotli.compress(rawdata)])
			bestsizelist.append([None, 'bz2', bz2.compress(rawdata)])
			if self.img_ctype == COL_TYPE_RGB_8 or self.img_ctype == COL_TYPE_RGBA_8:
				qoi_data = compress_qoi(self.img_ctype, rawdata, self.width, self.height)
				bestsizelist.append(['qoi', 'lzma', compress_lzma(qoi_data)])
				bestsizelist.append(['qoi', 'zlib', zlib.compress(qoi_data)])
				bestsizelist.append(['qoi', 'brotli', brotli.compress(qoi_data)])
				bestsizelist.append(['qoi', 'bz2', bz2.compress(qoi_data)])
				bestsizelist.append(['qoi', 'lz77', fastlz.compress(qoi_data)])
	
			rle_data = compress_sir8(self.img_ctype, rawdata)
			if rle_data: 
				bestsizelist.append(['sir8', 'lzma', compress_lzma(rle_data)])
				bestsizelist.append(['sir8', 'zlib', zlib.compress(rle_data)])
				bestsizelist.append(['sir8', 'brotli', brotli.compress(rle_data)])
				bestsizelist.append(['sir8', 'bz2', bz2.compress(rle_data)])
				bestsizelist.append(['sir8', 'lz77', fastlz.compress(rle_data)])

			rle_data = compress_sir16(self.img_ctype, rawdata)
			if rle_data: 
				bestsizelist.append(['sir16', 'lzma', compress_lzma(rle_data)])
				bestsizelist.append(['sir16', 'zlib', zlib.compress(rle_data)])
				bestsizelist.append(['sir16', 'brotli', brotli.compress(rle_data)])
				bestsizelist.append(['sir16', 'bz2', bz2.compress(rle_data)])
				bestsizelist.append(['sir16', 'lz77', fastlz.compress(rle_data)])

			bestsizelist = dict([[len(x[2]), x] for x in bestsizelist])
			self.compress_li_mode, self.compress_mode, self.img_data = bestsizelist[sorted(bestsizelist)[0]]
			return self.compress_li_mode or self.compress_mode

	def li_decompress(self):
		if self.compress_li_mode and not self.compress_mode:
			if 'qoi' == self.compress_li_mode: self.img_data = qoi.decode(self.img_data).tobytes()
			if 'sir16' == self.compress_li_mode: self.img_data = decompress_sir16(self.img_ctype, self.img_data)
			if 'sir8' == self.compress_li_mode: self.img_data = decompress_sir8(self.img_ctype, self.img_data)
			self.compress_li_mode = None

	def decompress(self):
		if self.compress_mode:
			if 'zlib' == self.compress_mode: self.img_data = zlib.decompress(self.img_data)
			elif 'lzma' == self.compress_mode: self.img_data = compression.lzma_decompress(self.img_data)
			elif 'brotli' == self.compress_mode: self.img_data = brotli.decompress(self.img_data)
			elif 'bz2' == self.compress_mode: self.img_data = bz2.decompress(self.img_data)
			elif 'lz77' == self.compress_mode: self.img_data = fastlz.decompress(self.img_data)
			self.compress_mode = None
		self.li_decompress()

	def from_pil_image(self, imgdata):
		image_mode = imgdata.mode
		self.width, self.height = imgdata.size

		self.img_data = imgdata.tobytes()

		if image_mode == '1': self.img_ctype = COL_TYPE_GRAY_1
		elif image_mode == 'L': self.img_ctype = COL_TYPE_GRAY_8
		elif image_mode == 'LA': self.img_ctype = COL_TYPE_GRAY_8A
		elif image_mode == 'I;16':
			self.img_ctype = COL_TYPE_GRAY_16
			self.img_data = np.frombuffer(self.img_data, '>H').tobytes()
		elif image_mode == 'P':
			imgdata = imgdata.convert('RGBA')
			image_mode = imgdata.mode
			self.img_data = imgdata.tobytes()
			self.img_ctype = COL_TYPE_RGBA_8
		elif image_mode == 'RGB': self.img_ctype = COL_TYPE_RGB_8
		elif image_mode == 'RGBA': self.img_ctype = COL_TYPE_RGBA_8
		else: print('unknown image_mode:', image_mode)

		self.img_org_ctype = self.img_ctype

		if image_mode == 'P':
			p_colortype, p_data = imgdata.palette.getdata()

			if p_colortype == 'RGB': 
				self.pal_data = np.frombuffer(p_data, 'B')

			if p_colortype == 'BGRX':
				palvals = np.frombuffer(p_data, np.uint8)
				palvals = np.reshape(palvals, (len(palvals)//4, 4))
				self.pal_data = palvals[:,[2,1,0]]
			self.pal_data = self.pal_data.reshape((-1, 3))
		return self.img_org_ctype

	def convert__rgb8a__gray8a(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_RGBA_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				tempdata = tempdata.reshape((self.width*self.height, 4))
				allsame = (tempdata[:,[0]]==tempdata[:,[1]]).flatten()
				allsame2 = (tempdata[:,[2]]==tempdata[:,[1]]).flatten()
				if all(allsame) and all(allsame2):
					self.img_data = tempdata[:,[0,3]].tobytes()
					self.img_ctype = COL_TYPE_GRAY_8A
					if VERBOSE_COLTYPECHANGE: print('---- rgb8a > gray8a')
					return True

	def convert__rgb8a__rgb8(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_RGBA_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				tempdata = tempdata.reshape((self.width*self.height, 4))
				if all(tempdata[:,[3]].flatten()==255):
					self.img_data = tempdata[:,[0,1,2]].tobytes()
					self.img_ctype = COL_TYPE_RGB_8
					if VERBOSE_COLTYPECHANGE: print('---- rgb8a > rgb8')
					return True

	def convert__rgb8a__index8a(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_RGBA_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				if (self.width*self.height)<=MAX_MEGAPIXEL_SMALLER:
					tempdata = tempdata.reshape((self.width*self.height, 4))
					uniq_val, uniq_inverse = np.unique(tempdata, axis=0, return_inverse=True)
					if len(uniq_val)<255:
						self.pal_ctype = COL_TYPE_RGBA_8
						self.pal_data = uniq_val.astype(np.uint8)
						self.img_ctype = COL_TYPE_INDEXA_8
						self.img_data = uniq_inverse.astype(np.uint8).tobytes()
						if VERBOSE_COLTYPECHANGE: print('---- rgb8a > index8a: %i colors' % len(self.pal_data))
						return True

	def convert__index8a__index4a(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_INDEXA_8:
				if len(self.pal_data)<16:
					intdata = np.frombuffer(self.img_data, 'B')
					intdata = compression.p_to_p4(intdata)
					self.img_data = intdata.tobytes()
					self.img_ctype = COL_TYPE_INDEXA_4
					if VERBOSE_COLTYPECHANGE: print('---- index8a > index4a: %i colors' % len(self.pal_data))
					return True

	def convert__rgb8a__index8sa(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_RGBA_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				if (self.width*self.height)<=MAX_MEGAPIXEL_SMALLER:
					tempdata = tempdata.reshape((self.width*self.height, 4))
					uniq_val, uniq_inverse = np.unique(tempdata[:,[0,1,2]], axis=0, return_inverse=True)
					if len(uniq_val)<255:
						self.pal_ctype = COL_TYPE_RGB_8
						self.pal_data = uniq_val.astype(np.uint8)
						self.img_ctype = COL_TYPE_INDEXSA_8
						outdata = np.zeros((self.width*self.height, 2), 'B')
						outdata[:,[0]] = uniq_inverse.astype(np.uint8).reshape(outdata[:,[0]].shape)
						outdata[:,[1]] = tempdata[:,[3]]
						self.img_data = outdata.tobytes()
						if VERBOSE_COLTYPECHANGE: print('---- rgb8a > index8sa: %i colors' % len(self.pal_data))
						return True

	def convert__gray8a__gray8(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_GRAY_8A:
				tempdata = np.frombuffer(self.img_data, 'B')
				tempdata = tempdata.reshape((self.width*self.height, 2))
				if all(tempdata[:,[1]].flatten()==255):
					self.img_data = tempdata[:,[0]].tobytes()
					self.img_ctype = COL_TYPE_GRAY_8
					if VERBOSE_COLTYPECHANGE: print('---- gray8a > gray8')
					return True

	def convert__rgb8__gray8(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_RGB_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				tempdata = tempdata.reshape((self.width, self.height, 3))
				allsame = (tempdata[:,:,[0]]==tempdata[:,:,[1]]).flatten()
				allsame2 = (tempdata[:,:,[2]]==tempdata[:,:,[1]]).flatten()
				if all(allsame) and all(allsame2):
					self.img_data = tempdata[:,:,[0]].tobytes()
					self.img_ctype = COL_TYPE_GRAY_8
					if VERBOSE_COLTYPECHANGE: print('---- rgb8 > gray8')
					return True

	def convert__rgb8__index8(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_RGB_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				if (self.width*self.height)<=MAX_MEGAPIXEL_SMALLER:
					tempdata = tempdata.reshape((self.width*self.height, 3))
					uniq_val, uniq_inverse = np.unique(tempdata, axis=0, return_inverse=True)
					if len(uniq_val)<255:
						self.pal_ctype = COL_TYPE_RGB_8
						self.pal_data = uniq_val.astype(np.uint8)
						self.img_ctype = COL_TYPE_INDEX_8
						self.img_data = uniq_inverse.astype(np.uint8).tobytes()
						if VERBOSE_COLTYPECHANGE: print('---- rgb8 > index8: %i colors' % len(self.pal_data))
						return True

	def convert__index8__index4(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_INDEX_8:
				datalen = len(self.pal_data)
				if self.pal_ctype == 'RGB': datalen = datalen//3
				if self.pal_ctype == 'BGRX': datalen = datalen//4
				if datalen<16: 
					self.img_ctype = COL_TYPE_INDEX_4
					intdata = np.frombuffer(self.img_data, 'B')
					intdata = compression.p_to_p4(intdata)
					self.img_data = intdata.tobytes()
					if VERBOSE_COLTYPECHANGE: print('---- Index8 > Index4')
					return True

	def convert__index8__index1(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_INDEX_8:
				datalen = len(self.pal_data)
				if self.pal_ctype == 'RGB': datalen = datalen//3
				if self.pal_ctype == 'BGRX': datalen = datalen//4
				if datalen<=2: 
					self.img_ctype = COL_TYPE_INDEX_1
					self.img_data = compression.p_to_p1(self.img_data, self.width, self.height)
					if VERBOSE_COLTYPECHANGE: print('---- Index8 > Index1')
					return True

	def convert__gray8a__bw8a(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_GRAY_8A:
				tempdata = np.frombuffer(self.img_data, 'B')
				tempdata = tempdata.reshape((self.width, self.height, 2))
				colorlevel = tempdata[:,:,[0]].flatten()
				alphalevel = tempdata[:,:,[1]].flatten()
				if all(colorlevel[alphalevel!=0]==255):
					self.img_ctype = COL_TYPE_WHITE_8A
					self.img_data = tempdata[:,:,[1]].tobytes()
					if VERBOSE_COLTYPECHANGE: print('---- gray8a > white8a')
				elif all(colorlevel[alphalevel!=0]==0):
					self.img_ctype = COL_TYPE_BLACK_8A
					self.img_data = tempdata[:,:,[1]].tobytes()
					if VERBOSE_COLTYPECHANGE: print('---- gray8a > black8a')

	def convert__gray8__gray4(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_GRAY_8:

				if (self.width*self.height)<=MAX_MEGAPIXEL_SMALLER:
					tempdata = np.frombuffer(self.img_data, 'B')
					uniq_val, uniq_inverse = np.unique(tempdata, axis=0, return_inverse=True)
					if len(uniq_val)<16:
						self.pal_ctype = COL_TYPE_GRAY_8
						self.pal_data = uniq_val
						self.img_ctype = COL_TYPE_GRAY_INDEX_4
						self.img_data = compression.p_to_p4(uniq_inverse.astype(np.uint8))
						if VERBOSE_COLTYPECHANGE: print('---- gray8 > gray4')

	def convert__gray8__gray1(self):
		if not self.is_compressed():
			if self.img_ctype == COL_TYPE_GRAY_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				tempdata = 1-(tempdata+1)
				if all((tempdata<2).flatten()):
					self.pal_ctype = COL_TYPE_RGB_8
					self.pal_data = []
					self.img_ctype = COL_TYPE_GRAY_1
					self.img_data = compression.p_to_p1(tempdata, self.width, self.height)
					if VERBOSE_COLTYPECHANGE: print('---- gray8 > gray1')

	def optimize(self):
		if not self.compress_mode:
			self.convert__rgb8a__gray8a()
			self.convert__rgb8a__rgb8()
			self.convert__rgb8a__index8a()
			self.convert__index8a__index4a()
			self.convert__rgb8a__index8sa()
			self.convert__gray8a__gray8()
			self.convert__rgb8__gray8()
			self.convert__rgb8__index8()
			self.convert__index8__index1()
			self.convert__index8__index4()
			self.convert__gray8a__bw8a()
			self.convert__gray8__gray1()
			self.convert__gray8__gray4()

	def make_pil_compat(self):
		if self.img_ctype == COL_TYPE_INDEXSA_8:
			if self.pal_ctype==COL_TYPE_RGBA_8:
				tempdata = np.frombuffer(self.img_data, 'B').reshape((-1, 2))
				pal_data = np.array(self.pal_data, 'B').reshape((-1, 3))

				outdata = np.zeros((self.width*self.height, 4), 'B')
				outdata[:,[0,1,2]] = pal_data[tempdata[:,[0]]].reshape(outdata[:,[0,1,2]].shape)
				outdata[:,[3]] = tempdata[:,[1]]

				self.img_data = outdata.tobytes()
				self.img_ctype = COL_TYPE_RGBA_8
				if VERBOSE_COLTYPECHANGE: print('---- index8sa > rgb8a')

		if self.img_ctype == COL_TYPE_INDEXA_4:
			if self.pal_ctype==COL_TYPE_RGBA_8:
				self.img_data = compression.p4_to_p(self.img_data)
				tempdata = np.frombuffer(self.img_data, 'B')
				pal_data = np.frombuffer(self.pal_data, 'B').reshape((-1, 4))
				self.img_data = pal_data[tempdata].tobytes()
				self.img_ctype = COL_TYPE_RGBA_8
				if VERBOSE_COLTYPECHANGE: print('---- index4a > rgb8a')

		if self.img_ctype == COL_TYPE_INDEXA_8:
			if self.pal_ctype==COL_TYPE_RGBA_8:
				tempdata = np.frombuffer(self.img_data, 'B')
				pal_data = np.frombuffer(self.pal_data, 'B').reshape((-1, 4))
				self.img_data = pal_data[tempdata].tobytes()
				self.img_ctype = COL_TYPE_RGBA_8
				if VERBOSE_COLTYPECHANGE: print('---- index8a > rgb8a')

		if self.img_ctype == COL_TYPE_INDEX_4:
			self.img_data = compression.p4_to_p(self.img_data)
			self.img_ctype = COL_TYPE_INDEX_8
			if VERBOSE_COLTYPECHANGE: print('---- index4 > index8')

		if self.img_ctype == COL_TYPE_INDEX_1:
			self.img_data = compression.p1_to_p(self.img_data, self.width, self.height)
			self.img_ctype = COL_TYPE_INDEX_8
			if VERBOSE_COLTYPECHANGE: print('---- index1 > index8')

		if self.img_ctype == COL_TYPE_WHITE_8A:
			tempdata = np.zeros((self.width*self.height, 2), 'B')
			tempdata[:,[0]] = 255
			tempdata[:,[1]] = np.frombuffer(self.img_data, 'B').reshape(tempdata[:,[1]].shape)
			self.img_ctype = COL_TYPE_GRAY_8A
			self.img_data = tempdata.tobytes()
			if VERBOSE_COLTYPECHANGE: print('---- white8a > gray8a')

		if self.img_ctype == COL_TYPE_BLACK_8A:
			tempdata = np.zeros((self.width*self.height, 2), 'B')
			tempdata[:,[0]] = 0
			tempdata[:,[1]] = np.frombuffer(self.img_data, 'B').reshape(tempdata[:,[1]].shape)
			self.img_ctype = COL_TYPE_GRAY_8A
			self.img_data = tempdata.tobytes()
			if VERBOSE_COLTYPECHANGE: print('---- black8a > gray8a')

		if self.img_ctype == COL_TYPE_GRAY_INDEX_4:
			self.img_ctype = COL_TYPE_RGB_8
			tempdata = np.frombuffer(compression.p4_to_p(self.img_data), 'B')
			pal_data = np.zeros((len(self.pal_data), 3), 'B')
			for n, x in enumerate(self.pal_data):
				pal_data[:][n] = self.pal_data[n]
			self.pal_data = pal_data
			self.img_data = pal_data[tempdata].tobytes()
			if VERBOSE_COLTYPECHANGE: print('---- gray4 > gray8')

	def to_pil_image(self, filename):
		self.decompress()
		imgdata = None

		self.make_pil_compat()

		if self.img_ctype == COL_TYPE_GRAY_1:
			imgdata = Image.frombytes('1', (self.width, self.height), self.img_data, 'raw')
		elif self.img_ctype == COL_TYPE_GRAY_8:
			imgdata = Image.frombytes('L', (self.width, self.height), self.img_data, 'raw')
		elif self.img_ctype == COL_TYPE_GRAY_8A:
			imgdata = Image.frombytes('LA', (self.width, self.height), self.img_data, 'raw')
		elif self.img_ctype == COL_TYPE_GRAY_16:
			imgdata = Image.frombytes('I;16', (self.width, self.height), self.img_data, 'raw')
		elif self.img_ctype == COL_TYPE_RGB_8:
			imgdata = Image.frombytes('RGB', (self.width, self.height), self.img_data, 'raw')
		elif self.img_ctype == COL_TYPE_RGBA_8:
			imgdata = Image.frombytes('RGBA', (self.width, self.height), self.img_data, 'raw')
		elif self.img_ctype == COL_TYPE_INDEX_8: 
			imgdata = Image.new('P', (self.width, self.height))
			imgdata.putpalette(self.pal_data)
			imgdata.frombytes(self.img_data)
		else: print('unknown img_ctype:', self.img_ctype)
		if imgdata is not None: imgdata.save(filename)

def compress_lzma(rawdata): 
	compressor = lzma.LZMACompressor()
	rawdata = compressor.compress(rawdata)
	rawdata += compressor.flush()
	return rawdata

OPTIMIZE_DATA = 1

def image_to_container(num, filepath, container_obj, compress_mode, cargsv): 
	try:
		imgdata = Image.open(filepath)
		with container_obj.add_container(num) as w:
			return imageobj_to_containerdata(imgdata, w, compress_mode, cargsv)
	except KeyboardInterrupt:
		exit()
	#except:
	#	import traceback
	#	print(traceback.format_exc())
	#	return 'ERROR', None

def imageobj_to_containerdata(imgdata, container_obj, compress_mode, cargsv): 
	#print('image_to_container', filename, compress_mode)
	container_obj.add_header_value(HEADER_ID__DATATYPE, T_UINT32, DATATYPE_IMAGE_SINGLE)

	peri_image = peridot_image()
	org_ctype = peri_image.from_pil_image(imgdata)
	peri_image.optimize()

	if 'filepath' in cargsv:
		filepath = cargsv['filepath']
		basename = os.path.basename(cargsv['filepath'])
		foldername = os.path.dirname(cargsv['filepath'])

		basename, filetype = os.path.splitext(basename)

		container_obj.add_value(ID_EDITOR_FILENAME, T_STRING, basename)
		container_obj.add_value(ID_EDITOR_FILETYPE, T_STRING, filetype)
		container_obj.add_value(ID_EDITOR_FILEPATH, T_STRING, foldername)

	container_obj.add_value(ID_EDITOR_ORG_COLORTYPE, T_STRING, org_ctype)

	container_obj.add_value(ID_COLOR, T_STRING, peri_image.img_ctype)
	container_obj.add_value_list(ID_SIZE, T_UINT32, [peri_image.width, peri_image.height])

	if 'filesize' in cargsv: orgsize = cargsv['filesize']
	else: orgsize = len(peri_image.img_data)

	compdone = False
	if compress_mode: 
		if 'best' in compress_mode: compdone = peri_image.compress_best()
		if not compdone and 'fast' in compress_mode: compdone = peri_image.compress_fast()
		if not compdone and 'vfast' in compress_mode: compdone = peri_image.compress_veryfast()
		if not compdone and 'qoi' in compress_mode: compdone = peri_image.li_compress('qoi', None)
		if not compdone and 'qoi:lzma' in compress_mode: compdone = peri_image.li_compress('qoi', 'lzma')
		if not compdone and 'qoi:zlib' in compress_mode: compdone = peri_image.li_compress('qoi', 'zlib')
		if not compdone and 'qoi:brotli' in compress_mode: compdone = peri_image.li_compress('qoi', 'brotli')
		if not compdone and 'qoi:bz2' in compress_mode: compdone = peri_image.li_compress('qoi', 'bz2')
		if not compdone and 'qoi:lz77' in compress_mode: compdone = peri_image.li_compress('qoi', 'lz77')
		if not compdone and 'sir8' in compress_mode: compdone = peri_image.li_compress('sir8', None)
		if not compdone and 'sir8:lzma' in compress_mode: compdone = peri_image.li_compress('sir8', 'lzma')
		if not compdone and 'sir8:zlib' in compress_mode: compdone = peri_image.li_compress('sir8', 'zlib')
		if not compdone and 'sir8:brotli' in compress_mode: compdone = peri_image.li_compress('sir8', 'brotli')
		if not compdone and 'sir8:bz2' in compress_mode: compdone = peri_image.li_compress('sir8', 'bz2')
		if not compdone and 'sir8:lz77' in compress_mode: compdone = peri_image.li_compress('sir8', 'bz2')
		if not compdone and 'sir16' in compress_mode: compdone = peri_image.li_compress('sir16', None)
		if not compdone and 'sir16:lzma' in compress_mode: compdone = peri_image.li_compress('sir16', 'lzma')
		if not compdone and 'sir16:zlib' in compress_mode: compdone = peri_image.li_compress('sir16', 'zlib')
		if not compdone and 'sir16:brotli' in compress_mode: compdone = peri_image.li_compress('sir16', 'brotli')
		if not compdone and 'sir16:bz2' in compress_mode: compdone = peri_image.li_compress('sir16', 'bz2')
		if not compdone and 'sir16:lz77' in compress_mode: compdone = peri_image.li_compress('sir16', 'lz77')
		if not compdone and 'zlib' in compress_mode: compdone = peri_image.compress('zlib')
		if not compdone and 'lzma' in compress_mode: compdone = peri_image.compress('lzma')
		if not compdone and 'brotli' in compress_mode: compdone = peri_image.compress('brotli')
		if not compdone and 'bz2' in compress_mode: compdone = peri_image.compress('bz2')

	compress_mode = peri_image.get_comptxt()
	if compress_mode: container_obj.add_value(ID_COMPRESSTYPE, T_STRING, compress_mode)

	if peri_image.img_ctype in [COL_TYPE_INDEX_8, COL_TYPE_INDEX_4, COL_TYPE_INDEX_1]:
		paldata = np.frombuffer(peri_image.pal_data, 'B').flatten()
		container_obj.add_value(ID_PALLETE_COLORTYPE, T_STRING, peri_image.pal_ctype)
		container_obj.add_value_list(ID_PALLETE_DATA, T_UINT8, paldata)

	if peri_image.img_ctype in [COL_TYPE_INDEXA_8, COL_TYPE_INDEXA_4, COL_TYPE_INDEXSA_8, COL_TYPE_GRAY_INDEX_4]:
		paldata = np.frombuffer(peri_image.pal_data, 'B').flatten()
		container_obj.add_value(ID_PALLETE_COLORTYPE, T_STRING, COL_TYPE_RGBA_8)
		container_obj.add_value_list(ID_PALLETE_DATA, T_UINT8, paldata)

	rawdata = peri_image.img_data
	if not compress_mode:
		colormode = peri_image.img_ctype

		if colormode == COL_TYPE_GRAY_8:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		elif colormode == COL_TYPE_GRAY_8A:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		elif colormode == COL_TYPE_GRAY_16:
			container_obj.add_value_list(ID_DATA, T_UINT16, np.frombuffer(rawdata, '<H'))
		elif colormode == COL_TYPE_INDEX_8:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		elif colormode == COL_TYPE_INDEXA_8:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		elif colormode == COL_TYPE_RGB_8:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		elif colormode == COL_TYPE_RGBA_8:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		elif colormode == COL_TYPE_WHITE_8A:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		elif colormode == COL_TYPE_BLACK_8A:
			container_obj.add_value_list(ID_DATA, T_UINT8, np.frombuffer(rawdata, 'B'))
		else: 
			container_obj.add_value(ID_DATA, T_BYTES, rawdata)
	else:
		container_obj.add_value(ID_DATA, T_BYTES, rawdata)

	return peri_image.img_ctype, peri_image.get_comptxt(), len(peri_image.img_data)/orgsize

def container_to_image(container_obj, filename, byr_stream): 

	peri_image = peridot_image()

	comptype = None

	for x in container_obj:
		if not x.is_header:
			idnume = x.id

			if idnume == ID_COLOR: peri_image.img_ctype = x.getvalue(byr_stream)
			if idnume == ID_SIZE: peri_image.width, peri_image.height = x.getvalue(byr_stream)
			if idnume == ID_COMPRESSTYPE: 
				compress_mode = x.getvalue(byr_stream).split(':')
				if len(compress_mode)==1: 
					if compress_mode[0] in ['qoi', 'sir16', 'sir8']: peri_image.compress_li_mode = compress_mode[0]
					else: peri_image.compress_mode = compress_mode[0]
				if len(compress_mode)==2: peri_image.compress_li_mode, peri_image.compress_mode = compress_mode
				comptype = peri_image.get_comptxt()
			if idnume == ID_PALLETE_COLORTYPE: peri_image.pal_ctype = x.getvalue(byr_stream)
			if idnume == ID_PALLETE_DATA: peri_image.pal_data = x.getvalue(byr_stream)
			if idnume == ID_DATA:
				imgdata = x.getvalue(byr_stream)
				img_data = peri_image.img_data = x.getvalue(byr_stream)
				img_ctype = peri_image.img_ctype

				if not comptype:
					if img_ctype == COL_TYPE_GRAY_8: peri_image.img_data = img_data.tobytes()
					if img_ctype == COL_TYPE_GRAY_8A: peri_image.img_data = img_data.tobytes()
					if img_ctype == COL_TYPE_GRAY_16: peri_image.img_data = img_data.tobytes()
					if img_ctype == COL_TYPE_RGB_8: peri_image.img_data = img_data.tobytes()
					if img_ctype == COL_TYPE_RGBA_8: peri_image.img_data = img_data.tobytes()
					if img_ctype == COL_TYPE_WHITE_8A: peri_image.img_data = img_data.tobytes()
					if img_ctype == COL_TYPE_BLACK_8A: peri_image.img_data = img_data.tobytes()
				peri_image.to_pil_image(filename)

	return peri_image.img_ctype, comptype