from objects.peridot_obj import *
from functions.datatype_image import *
import os

comptype = ['vfast']

container_obj = peridot_container()
container_obj.datatype = 'Topaz ImgPack'

import glob
paths = []
paths += glob.glob('G:\\Projects\\PeridotData\\imagepack_in\\**\\*.jpg', recursive=True)
paths += glob.glob('G:\\Projects\\PeridotData\\imagepack_in\\**\\*.tga', recursive=True)
paths += glob.glob('G:\\Projects\\PeridotData\\imagepack_in\\**\\*.png', recursive=True)
paths += glob.glob('G:\\Projects\\PeridotData\\imagepack_in\\**\\*.bmp', recursive=True)
paths += glob.glob('G:\\Projects\\PeridotData\\imagepack_in\\**\\*.gif', recursive=True)

for num, filename in enumerate(paths):
	if not os.path.isdir(filename):
		filesize = os.path.getsize(filename)

		image_mode, compdone, orgsize = image_to_container(num, filename, container_obj, comptype, filesize=filesize)
		print(' '*18, str(compdone).ljust(18), str(image_mode).ljust(10), (str(round(orgsize*100, 3))+'%').ljust(10), filename)

container_obj.write_to_file('imagepack.bin')
