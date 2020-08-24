import sys
import os
import shutil

MAYA_FORMAT = ['ma', 'mb']

def openAndProcessMayaFile(file_path, asset_name, source_base_proj_dir, proj_dir, proj_dict_str, file_format_dict_str):
    print 'openAndProcessMayaFile start'
    import maya.standalone as standalone
    standalone.initialize(name='python')

    global cmds
    import maya.cmds as cmds

    proj_dict = eval(proj_dict_str)
    FILE_FORMAT_DICT = eval(file_format_dict_str)
    file_extension = file_path.rpartition('.')[2]
    maya_format = FILE_FORMAT_DICT['ma']
    if file_extension == 'mb':
        maya_format = FILE_FORMAT_DICT['mb']

    if file_extension in MAYA_FORMAT:
        cmds.file(file_path, open=True, ignoreVersion=True, prompt=False)
        if cmds.ls(type='file', long=True):
            copyTextureFiles(source_base_proj_dir, proj_dir, proj_dict)
    else:
        cmds.file(file_path,
                  i=True,
                  ignoreVersion=True,
                  mergeNamespacesOnClash=False,
                  namespace=asset_name,
                  preserveReferences=True)
    scenes_dir_path = '%s/%s' % (proj_dir, proj_dict['scene'])
    new_file_name = '%s_v001_r001.ma' % asset_name
    new_scene_path = '%s/%s' % (scenes_dir_path, new_file_name)

    cmds.file(rename=new_scene_path)
    cmds.file(save=True, force=True, type=maya_format)

    cmds.file(new=True, force=True)

def copyTextureFiles(source_base_proj_dir, proj_dir, proj_dict):
    files_list = cmds.ls(type='file', long=True)
    print 'foreign_asset_manager output:', files_list
    for file_node in files_list:
        file_path = cmds.getAttr('%s.fileTextureName' % file_node)
        file_name = os.path.basename(file_path)
        found_dir = None
        for dir, subdirs, files in os.walk(source_base_proj_dir):
            if file_name in files:
                found_dir = dir.replace('\\', '/')
                break
        if not found_dir:
            continue
        new_source_file_path = '%s/%s' % (found_dir, file_name)
        textures_dir = proj_dict['images']
        dst_file_path = '%s/%s/%s' % (proj_dir, textures_dir, file_name)
        print 'copy: %s >> %s' % (new_source_file_path, dst_file_path)
        shutil.copy(new_source_file_path, dst_file_path)
        cmds.setAttr('%s.fileTextureName' % file_node, dst_file_path, type='string')

if __name__ == "__main__":
    openAndProcessMayaFile(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])