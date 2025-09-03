from objects.peridot_obj import *
from functions.datatype_image import *
import os

comptype = ['vfast']

container_obj = peridot_container()
container_obj.datatype = 'Topaz ImgPack'

startpath = '..\\imagepack_in'

import glob
paths = []
paths += glob.glob(startpath+'\\**\\*.jpg', recursive=True)
paths += glob.glob(startpath+'\\**\\*.tga', recursive=True)
paths += glob.glob(startpath+'\\**\\*.png', recursive=True)
paths += glob.glob(startpath+'\\**\\*.bmp', recursive=True)
paths += glob.glob(startpath+'\\**\\*.gif', recursive=True)

for num, filename in enumerate(paths):
	if not os.path.isdir(filename):
		filesize = os.path.getsize(filename)

		cargsv = {'filesize': filesize}
		cargsv['filepath'] = os.path.relpath(filename, startpath)

		image_mode, compdone, orgsize = image_to_container(num, filename, container_obj, comptype, cargsv)
		print(' '*18, str(compdone).ljust(18), str(image_mode).ljust(10), (str(round(orgsize*100, 3))+'%').ljust(10), filename)

container_obj.write_to_file('../imagepack.bin')
