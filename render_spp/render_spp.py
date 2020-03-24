#!/usr/bin/env python3

import os
import sys
import shutil
from timeit import default_timer as timer
import json

if len(sys.argv) < 4:
	print('Usage: render_spp.py tungsten_bin scene.json "1 2 4 8..." [-d]')
	exit(0)

tungsten_bin = sys.argv[1]
scene_file = sys.argv[2]
spps = sys.argv[3].split()
make_dir = False
if len(sys.argv) == 5:
	make_dir = (sys.argv[4] == '-d')

if not os.path.exists(tungsten_bin) and not shutil.which(tungsten_bin):
	print('Tungsten binary file does not exist: ' + tungsten_bin)
	exit(1)

if os.path.exists(scene_file):
	with open(scene_file, 'r') as f:
		scene_str = f.read()
else:
	print('Scene file does not exist: ' + scene_file)
	exit(1)

def StrIsInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False

for spp in spps:
	if not StrIsInt(spp):
		print('Invalid SPP count: ' + spp)
		exit(1)

scene_json = json.loads(scene_str)

dir_name = os.path.dirname(scene_file)
exr_file_name = scene_json["renderer"]["hdr_output_file"]
exr_file = os.path.join(dir_name, exr_file_name)
exr_file_name_stem, _ = os.path.splitext(exr_file_name)
exr_file_stem = os.path.join(dir_name, exr_file_name_stem)

scene_file_stem, _ = os.path.splitext(scene_file)

start = timer()
for spp in spps:
	scene_file_stem_new = scene_file_stem + '_' + spp
	scene_file_new = scene_file_stem_new + '.json'
	scene_json["renderer"]["spp"] = int(spp)
	scene_str_new = json.dumps(scene_json)
	with open(scene_file_new, 'w') as f:
		f.write(scene_str_new)
	os.system(tungsten_bin + ' ' + scene_file_new)
	os.remove(scene_file_new)
	exr_file_stem_new = exr_file_stem + '_' + spp
	exr_file_new = exr_file_stem_new + '.exr'
	os.rename(exr_file, exr_file_new)
	if make_dir:
		if not os.path.exists(exr_file_stem_new):
			os.mkdir(exr_file_stem_new)
		os.system("mv " + os.path.join(dir_name, '*.exr') + " " + exr_file_stem_new)
end = timer()

duration = int(end - start)
ss = end - start - duration
s = duration % 60
m = duration / 60 % 60
h = duration / 3600
print('\nTotal Time: %02d:%02d:%05.2f' % (h, m, s + ss))
