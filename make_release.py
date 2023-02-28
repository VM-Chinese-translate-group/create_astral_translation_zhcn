#!/usr/bin/env python3
import zipfile
import glob, os, shutil
from handle_hard_coding import start_handle_hard_coding

def copy_tree(src, dst, symlinks=False, ignore=None):
	if not os.path.exists(dst):
		os.makedirs(dst)
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			copy_tree(s, d, symlinks, ignore)
		else:
			if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
				shutil.copy2(s, d)

def add_dir_to_zipfile(zip_obj, zip_fp):
	def add_objs(files, zip_fp, base_dir = '.'):
		for file in files:
			if os.path.isfile(file):
				arcname = os.path.join(base_dir, os.path.basename(file))
			else:
				arcname = base_dir
			zip_fp.write(file, arcname)
	
	zip_obj_dir = os.path.dirname(zip_obj)
	for folder_name, sub_folders, files in os.walk(zip_obj):
		base_dir = folder_name.replace(zip_obj_dir, '')
		add_objs([folder_name], zip_fp, base_dir)
		files_path = [os.path.join(folder_name, file) for file in files]
		add_objs(files_path, zip_fp, base_dir)

if __name__ == "__main__":
	work_dir = os.path.dirname(os.path.abspath(__file__))
	src_dir = os.path.join(work_dir, 'v2.0')
	release_name = 'release'
	release_dir = os.path.join(work_dir, 'release')
	resourcepack_name = 'create_astral_translation'
	resourcepack_path = os.path.join(src_dir, 'resourcepacks', resourcepack_name)

	# Required directories
	required_dirs = ['resourcepacks', 'config', 'kubejs', 'global_packs']
	
	# Make Dirs
	if not os.path.isdir(release_dir): os.makedirs(release_dir)
	for required_dir in required_dirs:
		required_path = os.path.join(release_dir, required_dir)
		if not os.path.isdir(required_path): 
			os.makedirs(required_path)

	# Handle Hard Coding and Copy to Release Dir
	## KubeJS startup.js, FTB Quests, Custom Machinery
	official_dir = os.path.join(work_dir, "Create-Astral")
	start_handle_hard_coding(official_dir, release_dir)

	# Resourcepack
	os.chdir(resourcepack_path)
	jsons = glob.glob("assets/*/lang/zh_cn.json")
	resourcepack_zip = os.path.join(release_dir, 'resourcepacks', f'{resourcepack_name}.zip')
	with zipfile.ZipFile(resourcepack_zip, 'w', zipfile.ZIP_DEFLATED) as zip_fp:
		for json in jsons:
			zip_fp.write(json)
		zip_fp.write('pack.png')
		zip_fp.write('pack.mcmeta')
		
	# Pack All to a Zip File
	md_files = ['changelog.md', 'README.md']
	os.chdir(release_dir)
	release_zip = os.path.join(release_dir, f'{release_name}.zip')
	with zipfile.ZipFile(release_zip, 'w', zipfile.ZIP_DEFLATED) as zip_fp:
		for required_dir in required_dirs:
			add_dir_to_zipfile(required_dir, zip_fp)
		for md_file in md_files:
			md_path = os.path.join(work_dir, md_file)
			zip_fp.write(md_path, arcname = md_file)
	
	# Delete Temp Files
	for required_dir in required_dirs:
		required_path = os.path.join(release_dir, required_dir)
		shutil.rmtree(required_path)
	
	print('[INFO] All is done!')