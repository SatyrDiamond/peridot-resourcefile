
from objects.data_bytes import bytewriter
from objects.data_bytes import bytereader
import numpy as np
import rle
import io

def p_to_p4(imgdata): 
	oimgdata = np.zeros((len(imgdata)/2).__ceil__(), 'B')
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

def rle_getv(rawdata): 
	tempdata = np.frombuffer(rawdata, 'B')
	rle_vals, rle_repeats = rle.encode(tempdata)
	rle_vals = np.array(rle_vals, 'B')
	rle_repeats = np.array(rle_repeats, 'I')
	valrep = np.zeros(len(rle_repeats), np.dtype([('vals', np.uint8), ('repeats', np.uint32)]))
	valrep['vals'] = rle_vals
	valrep['repeats'] = rle_repeats
	return valrep

def lzma_decompress(data): 
	import lzma
	obj = lzma.LZMADecompressor()
	data = obj.decompress(data)
	return data

def compress_rle8c_256(rawdata): 
	orgsize = len(rawdata)
	valrep = rle_getv(rawdata)

	invalrep = rle_getv(valrep['repeats']>1)
	vals = valrep['vals']
	countv = 0

	f = bytewriter.bytewriter()
	for inlong, inrepeats in invalrep:
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

	return f.getvalue()

def compress_rle8c_16(rawdata): 
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
	return f.getvalue()

def internal__comp_rle4c_valmake(value, size): 
	return (int(value)<<4) + int(size)

def internal__comp_rle4c_writerepeat(value, repeats, f): 
	f.uint8(internal__comp_rle4c_valmake(value, min(repeats, 0xf)))
	if repeats>=0xf:
		f.varint(max(0, repeats//0xf))
		repeatremaining = repeats%0xf
		if repeatremaining: f.uint8(internal__comp_rle4c_valmake(value, repeatremaining))

def compress_rle4c(rawdata): 
	orgsize = len(rawdata)
	f = bytewriter.bytewriter()
	valrep = rle_getv(p4_to_p(rawdata))
	for value, repeats in valrep:
		if f.end<orgsize: internal__comp_rle4c_writerepeat(value, repeats, f)
		else: return None
	return f.getvalue()

def decompress_rle8c_256(rawdata):
	b_in = bytereader.bytereader(rawdata)
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

def decompress_rle8c_16(rawdata):
	b_in = bytereader.bytereader(rawdata)
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

def decompress_rle4c(rawdata):
	b_in = bytereader.bytereader(rawdata)
	b_out = io.BytesIO()
	while b_in.remaining():
		v = b_in.uint8()
		value = v>>4
		repeats = v&0xf
		repeatmax = 0
		if repeats==0xf: repeats *= b_in.varint()
		o = np.zeros(repeats, np.uint8)
		o[:] = value
		b_out.write(o.tobytes())
	outdata = b_out.getvalue()
	intdata = np.frombuffer(outdata, 'B')
	outdata = p_to_p4(intdata).tobytes()
	return outdata



def compress_rle8c_256_old(rawdata): 
	orgsize = len(rawdata)
	valrep = rle_getv(rawdata)

	f = bytewriter.bytewriter()
	for value, repeats in valrep:
		if f.end<orgsize:
			f.varint(repeats)
			f.uint8(value)
		else:
			return None
	return f.getvalue()

def compress_rle4c_useless(rawdata): 
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
					#print('REPEAT', value, repeats)
					internal__comp_rle4c_writerepeat(value, repeats, f)
					countv += 1
			else:
				value = vals[countv:countv+inrepeats]
				repraw = max(inrepeats, 0xf)
				#print('RAW', value, inrepeats)
				f.uint8(internal__comp_rle4c_valmake(repraw, 0))
				if inrepeats>=0xf: f.varint(inrepeats-0xf)
				f.l_uint8( p_to_p4(value), (inrepeats/2).__ceil__())
				countv += inrepeats

	return f.getvalue()
