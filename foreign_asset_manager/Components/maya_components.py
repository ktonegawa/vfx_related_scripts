import os
import subprocess

import maya.cmds as cmds
import pymel.core as pm

WORKSPACE_FILE = 'workplace.mel'
MAYAPY_PATH = 'C:/Program Files/Autodesk/Maya2016.5/bin/mayapy.exe'
MAYAPY_COMPONENT_FILE = '%s/mayapy_component.py' % os.path.dirname(__file__)
FILE_FORMAT_DICT = {'abc': 'Alembic',
                    'fbx': 'FBX',
                    'ma': 'mayaAscii',
                    'mb': 'mayaBinary',
                    'obj': 'OBJ',
                    'stl': 'STL_ATF'}

class MayaOperationClass(object):
    def __init__(self):
        pass

    def createFolder(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def buildProject(self, AssetClassObj):
        workspace_file_content = '//Custom Maya Project Definition\n\n' \
                                'workspace -fr \"scene\" \"{scenes}\";\n' \
                                'workspace -fr \"mayaAscii\" \"{scenes}\";\n' \
                                'workspace -fr \"mayaBinary\" \"{scenes}\";\n' \
                                'workspace -fr \"sourceImages\" \"{sourceimages}\";\n' \
                                'workspace -fr \"images\" \"{textures}\";\n' \
                                'workspace -fr \"Alembic\" \"{cache}\";\n' \
                                'workspace -fr \"OBJ\" \"{cache}\";\n' \
                                'workspace -fr \"OBJexport\" \"{cache}\";\n' \
                                'workspace -fr \"FBX\" \"{cache}\";\n' \
                                'workspace -fr \"renderData\" \"{renders}\";\n' \
                                'workspace -fr \"movie\" \"movies\";\n' \
                                'workspace -fr \"scripts\" \"scripts\";\n' \
                                'workspace -fr \"furEqualMap\" \"renderData/fur/furEqualMap\";\n' \
                                'workspace -fr \"move\" \"data\";\n' \
                                'workspace -fr \"autoSave\" \"autosave\";\n' \
                                'workspace -fr \"sound\" \"sound\";\n' \
                                'workspace -fr \"iprImages\" \"renderData/iprImages\";\n' \
                                'workspace -fr \"shaders\" \"renderData/shaders\";\n' \
                                'workspace -fr \"furFiles\" \"renderData/fur/furFiles\";\n' \
                                'workspace -fr \"offlineEdit\" \"scenes/edits\";\n' \
                                'workspace -fr \"furShadowMap\" \"renderData/fur/furShadowMap\";\n' \
                                'workspace -fr \"fileCache\" \"cache/nCache\";\n' \
                                'workspace -fr \"eps\" \"data\";\n' \
                                'workspace -fr \"fluidCache\" \"cache/nCache/fluid\";\n' \
                                'workspace -fr \"3dPaintTextures\" \"sourceimages/3dPaintTextures\";\n' \
                                'workspace -fr \"mel\" \"scripts\";\n' \
                                'workspace -fr \"translatorData\" \"data\";\n' \
                                'workspace -fr \"particles\" \"cache/particles\";\n' \
                                'workspace -fr \"furImages\" \"renderData/fur/furImages\";\n' \
                                'workspace -fr \"clips\" \"clips\";\n' \
                                'workspace -fr \"depth\" \"renderData/depth\";\n' \
                                'workspace -fr \"audio\" \"sound\";\n' \
                                'workspace -fr \"bifrostCache\" \"cache/bifrost\";\n' \
                                'workspace -fr \"illustrator\" \"data\";\n' \
                                'workspace -fr \"diskCache\" \"data\";\n' \
                                'workspace -fr \"templates\" \"assets\";\n' \
                                'workspace -fr \"furAttrMap\" \"renderData/fur/furAttrMap\";\n'.format(scenes=AssetClassObj.scenes_dir,
                                                                                                       sourceimages=AssetClassObj.sourceimages_dir,
                                                                                                       textures=AssetClassObj.textures_dir,
                                                                                                       cache=AssetClassObj.cache_dir,
                                                                                                       renders=AssetClassObj.renders_dir)

        workspace_file = '%s/workspace.mel' % AssetClassObj.dir
        if not os.path.isdir(AssetClassObj.dir):
            os.makedirs(AssetClassObj.dir)
        with open(workspace_file, 'w') as file_to_write:
            file_to_write.write(workspace_file_content)
        pm.mel.eval(r' setProject "{}"'.format(AssetClassObj.dir))

        proj_dict = dict()

        for file_rule in cmds.workspace(query=True, fileRuleList=True):
            file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
            proj_dict[file_rule] = file_rule_dir
            maya_file_rule_dir = '%s/%s' % (AssetClassObj.dir, file_rule_dir)
            self.createFolder(maya_file_rule_dir)

        file_extension = AssetClassObj.source_file.rpartition('.')[2]
        file_type = FILE_FORMAT_DICT[file_extension]

        process = subprocess.Popen('"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (MAYAPY_PATH,
                                                                            MAYAPY_COMPONENT_FILE,
                                                                            AssetClassObj.source_file,
                                                                            AssetClassObj.name,
                                                                            AssetClassObj.source_base_dir,
                                                                            AssetClassObj.dir,
                                                                            proj_dict,
                                                                            FILE_FORMAT_DICT),
                                                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        print err
        print out

    def openMayaFileNormally(self, name, file_path):
        if cmds.file(query=True, modified=True):
            current_file_path = cmds.file(query=True, sceneName=True)
            save_choice = cmds.confirmDialog(title='Save file?',
                                           message='Save the changes to file: \n'
                                                   '%s?' % current_file_path,
                                           button=['Save', 'Don\'t Save', 'Cancel'],
                                           defaultButton='Save',
                                           cancelButton='Don\'t Save',
                                           dismissString='Cancel')
            if save_choice == 'Save':
                cmds.file(save=True)
            elif save_choice == 'Cancel':
                return
        open_option = cmds.confirmDialog(title='Open Option',
                                           message='How to open this file?',
                                           button=['Open', 'Import', 'Reference'],
                                           defaultButton='Open')
        if open_option == 'Open':
            cmds.file(file_path, open=True, ignoreVersion=True, force=True)
        elif open_option == 'Import':
            cmds.file(file_path, i=True, ignoreVersion=True, renameAll=True, mergeNamespacesOnClash=True, namespace=name, force=True)
        elif open_option == 'Reference':
            cmds.file(file_path, reference=True, ignoreVersion=True, groupLocator=True, mergeNamespacesOnClash=True, namespace=name, force=True)


    def createThumbnail(self, destination):
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
        current_time = cmds.currentTime(query=True)
        file_path = '%s/preview_image.jpg' % destination
        cmds.playblast(viewer=False,
                       frame=current_time,
                       width=100,
                       height=100,
                       percent=100,
                       forceOverwrite=True,
                       showOrnaments=False,
                       format="image",
                       completeFilename=file_path)
        return file_path