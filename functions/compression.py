
from objects.data_bytes import bytewriter
from objects.data_bytes import bytereader
from PIL import Image
import numpy as np
import rle
import io

def max4len(val): 
	return (val/2).__ceil__()

def p1_to_p(imgdata, width, height): 
	imgdata = Image.frombytes('1', (width, height), imgdata, 'raw')
	imgdata = np.frombuffer(imgdata.convert('L').tobytes(), 'B')
	imgdata = (imgdata>0).astype(np.uint8)
	return imgdata.tobytes()

def p_to_p1(imgdata, width, height): 
	imgdata = np.frombuffer(imgdata, 'B')
	imgdata = (imgdata!=0).astype(np.uint8)*255
	imgdata = Image.frombytes('L', (width, height), imgdata, 'raw')
	return imgdata.convert('1').tobytes()

def p_to_p4(imgdata): 
	oimgdata = np.zeros(max4len(len(imgdata)), 'B')
	firstd = imgdata[0::2]
	secondd = imgdata[1::2]
	oimgdata[0:len(firstd)] = firstd<<4
	oimgdata[0:len(secondd)] += secondd
	return oimgdata

def p4_to_p(imgdata): 
	imgdata = np.frombuffer(imgdata, 'B')
	oimgdata = np.zeros(len(imgdata)*2, 'B')
	oimgdata[0::2] = (imgdata&0xF0)>>4
	oimgdata[1::2] = (imgdata&0x0F)
	return oimgdata

def lzma_decompress(data): 
	import lzma
	obj = lzma.LZMADecompressor()
	data = obj.decompress(data)
	return data

def rle_getv(rawdata): 
	tempdata = np.frombuffer(rawdata, 'B')
	return rle_getv_int(tempdata)

def rle_getv_int(intdata): 
	rle_vals, rle_repeats = rle.encode(intdata)
	rle_vals = np.array(rle_vals, 'B')
	rle_repeats = np.array(rle_repeats, 'I')
	valrep = np.zeros(len(rle_repeats), np.dtype([('vals', np.uint8), ('repeats', np.uint32)]))
	valrep['vals'] = rle_vals
	valrep['repeats'] = rle_repeats
	return valrep

def compress_sir16a_256(rawdata): 
	intdata = np.frombuffer(rawdata, 'B')
	int_gray = intdata[0::2].tobytes()
	int_alpha = intdata[1::2].tobytes()

	comp_gray = compress_sir16_256(int_gray)
	comp_alpha = compress_sir16_256(int_alpha)
	if comp_gray and comp_alpha:
		f = bytewriter.bytewriter()
		f.uint32(len(rawdata))
		f.uint32(len(comp_gray))
		f.raw(comp_gray)
		f.uint32(len(comp_alpha))
		f.raw(comp_alpha)
		return b'sir16a_256'+f.getvalue()

def decompress_sir16a_256(rawdata): 
	b_in = bytereader.bytereader(rawdata)
	b_in.magic_check(b'sir16a_256')
	o = np.zeros(b_in.uint32(), np.uint8)
	comp_gray = decompress_sir16_256(b_in.raw(b_in.uint32()))
	comp_alpha = decompress_sir16_256(b_in.raw(b_in.uint32()))
	o[0::2] = np.frombuffer(comp_gray, 'B')
	o[1::2] = np.frombuffer(comp_alpha, 'B')
	return o.tobytes()

def compress_sir16_256(intdata): 
	intdata = np.frombuffer(intdata, 'B')
	orgsize = len(intdata)
	valrep = rle_getv(intdata)
	vals = valrep['vals']
	countv = 0
	f = bytewriter.bytewriter()
	for inlong, inrepeats in rle_getv(valrep['repeats']>1):
		if f.end<orgsize:
			if inlong==1:
				for x in range(inrepeats):
					value, repeats = valrep[countv]
					f.varint(repeats)
					f.uint8(value)
					countv += 1
			else:
				f.varint(0)
				f.varint(inrepeats)
				f.l_uint8(vals[countv:countv+inrepeats], inrepeats)
				countv += inrepeats
		else:
			return None
	return b'sir16_256'+f.getvalue()

def compress_sir16_256_old(rawdata): 
	orgsize = len(rawdata)
	valrep = rle_getv(rawdata)

	f = bytewriter.bytewriter()
	for value, repeats in valrep:
		if f.end<orgsize:
			f.varint(repeats)
			f.uint8(value)
		else:
			return None
	return b'sir16_256'+f.getvalue()

def compress_sir16_16(rawdata): 
	orgsize = len(rawdata)
	valrep = rle_getv(p4_to_p(rawdata))
	f = bytewriter.bytewriter()
	for value, repeats in valrep:
		repeats = int(repeats)
		outval = (int(value)<<12)+min(repeats, 0xfff)
		if f.end<orgsize:
			f.uint16(outval)
			if repeats>=0xfff:
				f.varint(max(0, repeats//0xfff))
				repeatremaining = repeats%0xfff
				if repeatremaining:
					outval = (int(value)<<12) + int(repeatremaining)
					f.uint16(outval)
		else:
			return None
	return b'sir16__16'+f.getvalue()

def decompress_sir16_256(rawdata):
	b_in = bytereader.bytereader(rawdata)
	b_in.magic_check(b'sir16_256')
	b_out = io.BytesIO()
	while b_in.remaining():
		repeats = b_in.varint()
		if repeats:
			o = np.zeros(repeats, np.uint8)
			o[:] = b_in.uint8()
			b_out.write(o.tobytes())
		else:
			o = np.frombuffer(b_in.raw(b_in.varint()), np.uint8)
			b_out.write(o.tobytes())
	return b_out.getvalue()

def decompress_sir16_16(rawdata):
	b_in = bytereader.bytereader(rawdata)
	b_in.magic_check(b'sir16__16')
	b_out = io.BytesIO()
	while b_in.remaining():
		v = b_in.uint16()
		value = v>>12
		repeats = v&0xfff
		repeatmax = 0
		if repeats==0xfff: repeats *= b_in.varint()
		o = np.zeros(repeats, np.uint8)
		o[:] = value
		b_out.write(o.tobytes())
	outdata = b_out.getvalue()
	intdata = np.frombuffer(outdata, 'B')
	outdata = p_to_p4(intdata).tobytes()
	return outdata



def internal__comp_sir8_valmake(value, size): 
	return (int(value)<<4) + int(size)

def internal__comp_sir8_writerepeat(value, repeats, f): 
	f.uint8(internal__comp_sir8_valmake(value, min(repeats, 0xf)))
	if repeats>=0xf:
		f.varint(max(0, repeats//0xf))
		repeatremaining = repeats%0xf
		if repeatremaining: f.uint8(internal__comp_sir8_valmake(value, repeatremaining))

def compress_sir8(rawdata): 
	orgsize = len(rawdata)
	f = bytewriter.bytewriter()
	valrep = rle_getv(p4_to_p(rawdata))
	for value, repeats in valrep:
		if f.end<orgsize: internal__comp_sir8_writerepeat(value, repeats, f)
		else: return None
	return b'sir8__16'+f.getvalue()

def compress_sir8_other(rawdata): 
	orgsize = len(rawdata)
	f = bytewriter.bytewriter()
	valrep = rle_getv(p4_to_p(rawdata))

	invalrep = rle_getv(valrep['repeats']>1)
	vals = valrep['vals']
	countv = 0

	for inlong, inrepeats in invalrep:
		if f.end<orgsize:
			if inlong==1: 
				for x in range(inrepeats):
					value, repeats = valrep[countv]
					internal__comp_sir8_writerepeat(value, repeats, f)
					countv += 1
			else:
				v = valrep[countv:countv+inrepeats]
				outvals = v['vals']
				lenvals = len(outvals)
				internal__comp_sir8_writerepeat(min(0xf, lenvals), 0, f)
				if lenvals==0xf: f.varint(lenvals-0xf)
				f.raw(p_to_p4(outvals))
				countv += inrepeats

	return b'sir8__16'+f.getvalue()

def decompress_sir8(rawdata):
	b_in = bytereader.bytereader(rawdata)
	b_in.magic_check(b'sir8__16')
	b_out = io.BytesIO()
	while b_in.remaining():
		v = b_in.uint8()
		value = v>>4
		repeats = v&0xf
		repeatmax = 0
		if repeats==0xf: repeats *= b_in.varint()
		if repeats:
			o = np.zeros(repeats, np.uint8)
			o[:] = value
			b_out.write(o.tobytes())
		else:
			sized = value
			if sized==0xf: sized += b_in.varint()
			nonrepd = b_in.raw(max4len(sized))
			nonrepd = p4_to_p(nonrepd)[0:sized]
			b_out.write(nonrepd.tobytes())

	outdata = b_out.getvalue()
	intdata = np.frombuffer(outdata, 'B')
	outdata = p_to_p4(intdata).tobytes()
	return outdata
