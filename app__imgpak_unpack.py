from objects.peridot_obj import *
from functions.datatype_image import *
import sys
import os

container_obj = peridot_container()
byr_stream = container_obj.read_from_file('../imagepack.bin', doload=0)
numo = len(container_obj.data)
for n, x in enumerate(container_obj):

	foldpath = ''
	filetype = '.png'
	filename = str(x.id)

	for i in x.getvalue(byr_stream, doload=0):
		if i.id == ID_EDITOR_FILENAME: filename = i.getvalue(byr_stream)
		if i.id == ID_EDITOR_FILETYPE: filetype = i.getvalue(byr_stream)
		if i.id == ID_EDITOR_FILEPATH: foldpath = i.getvalue(byr_stream)
	foldpath = '../imagepack_out/'+foldpath
	filepath = os.path.join(foldpath, filename+filetype)
	os.makedirs(foldpath, exist_ok=True)

	image_mode, compdone = container_to_image(x.getvalue(byr_stream), filepath, byr_stream)

	print(' '*18, str(compdone).ljust(18), str(image_mode).ljust(10), filename)

	#sys.stdout.write('\rImages %d of %d (%d%%)' % (n, numo, (n/numo)*100))
	#sys.stdout.flush()