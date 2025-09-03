from objects.peridot_obj import *
from functions.datatype_image import *

container_obj = peridot_container()
byr_stream = container_obj.read_from_file('imagepack.bin', doload=0)
for x in container_obj:
	filename = str(x.id)+'.png'
	for i in x.getvalue(byr_stream, doload=0):
		if i.id == 100: filename = i.getvalue(byr_stream)+'__'+str(x.id)+'.png'
	image_mode, compdone = container_to_image(x.getvalue(byr_stream), 'imagepack_out/'+filename, byr_stream)
	print(' '*18, str(compdone).ljust(18), str(image_mode).ljust(10), filename)
