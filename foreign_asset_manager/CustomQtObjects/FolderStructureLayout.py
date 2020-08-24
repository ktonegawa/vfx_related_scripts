from foreign_asset_manager import QtGui, QtCore

class FolderStructureLayout(QtGui.QFormLayout):
    def __init__(self, parent=None):
        super(FolderStructureLayout, self).__init__(parent)
        self.settings = QtCore.QSettings('settings.ini', QtCore.QSettings.IniFormat)
        self.base_dir_label = QtGui.QLabel('Base Project Dir')
        self.setWidget(0, QtGui.QFormLayout.LabelRole, self.base_dir_label)

        self.base_dir_lineEdit = QtGui.QLineEdit()
        self.setWidget(0, QtGui.QFormLayout.FieldRole, self.base_dir_lineEdit)

        self.scene_label = QtGui.QLabel('scene')
        self.setWidget(1, QtGui.QFormLayout.LabelRole, self.scene_label)

        self.scene_lineEdit = QtGui.QLineEdit()
        self.setWidget(1, QtGui.QFormLayout.FieldRole, self.scene_lineEdit)

        self.textures_label = QtGui.QLabel('textures')
        self.setWidget(2, QtGui.QFormLayout.LabelRole, self.textures_label)

        self.textures_lineEdit = QtGui.QLineEdit()
        self.setWidget(2, QtGui.QFormLayout.FieldRole, self.textures_lineEdit)

        self.sourceimages_label = QtGui.QLabel('sourceimages')
        self.setWidget(3, QtGui.QFormLayout.LabelRole, self.sourceimages_label)

        self.sourceimages_lineEdit = QtGui.QLineEdit()
        self.setWidget(3, QtGui.QFormLayout.FieldRole, self.sourceimages_lineEdit)

        self.references_label = QtGui.QLabel('references')
        self.setWidget(4, QtGui.QFormLayout.LabelRole, self.references_label)

        self.references_lineEdit = QtGui.QLineEdit()
        self.setWidget(4, QtGui.QFormLayout.FieldRole, self.references_lineEdit)

        self.cache_label = QtGui.QLabel('cache')
        self.setWidget(5, QtGui.QFormLayout.LabelRole, self.cache_label)

        self.cache_lineEdit = QtGui.QLineEdit()
        self.setWidget(5, QtGui.QFormLayout.FieldRole, self.cache_lineEdit)

        self.renders_label = QtGui.QLabel('renders')
        self.setWidget(6, QtGui.QFormLayout.LabelRole, self.renders_label)

        self.renders_lineEdit = QtGui.QLineEdit()
        self.setWidget(6, QtGui.QFormLayout.FieldRole, self.renders_lineEdit)

    def setDefaults(self):
        self.base_dir_lineEdit.setText('D:/PC6/Documents/maya/projects/default')
        self.scene_lineEdit.setText('scenes')
        self.textures_lineEdit.setText('textures')
        self.sourceimages_lineEdit.setText('sourceimages')
        self.references_lineEdit.setText('references')
        self.cache_lineEdit.setText('cache')
        self.renders_lineEdit.setText('renders')

    def readFromSettings(self):
        self.base_dir_lineEdit.setText(self.settings.value('base_path', type=str))
        self.scene_lineEdit.setText(self.settings.value('scenes', type=str))
        self.textures_lineEdit.setText(self.settings.value('textures', type=str))
        self.sourceimages_lineEdit.setText(self.settings.value('sourceimages', type=str))
        self.references_lineEdit.setText(self.settings.value('references', type=str))
        self.cache_lineEdit.setText(self.settings.value('cache', type=str))
        self.renders_lineEdit.setText(self.settings.value('renders', type=str))

    def saveSettings(self):
        self.settings.setValue('base_path', self.base_dir_lineEdit.text())
        self.settings.setValue('scenes', self.scene_lineEdit.text())
        self.settings.setValue('textures', self.textures_lineEdit.text())
        self.settings.setValue('sourceimages', self.sourceimages_lineEdit.text())
        self.settings.setValue('references', self.references_lineEdit.text())
        self.settings.setValue('cache', self.cache_lineEdit.text())
        self.settings.setValue('renders', self.renders_lineEdit.text())