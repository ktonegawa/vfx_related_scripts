import os

from foreign_asset_manager.CustomQtObjects.FolderStructureLayout import FolderStructureLayout

from foreign_asset_manager import QtGui

class Wizard(QtGui.QWizard):
    def __init__(self):
        super(Wizard, self).__init__()
        self.setWindowTitle("Add Foreign Asset")
        self.first_page = AddAssetWizardPage1()
        self.second_page = AddAssetWizardPage2()
        self.third_page = AddAssetWizardPage3()
        self.addPage(self.first_page)
        self.addPage(self.second_page)
        self.addPage(self.third_page)
        self.button(QtGui.QWizard.NextButton).clicked.connect(self.customNextFunc)

    def customNextFunc(self):
        if self.currentPage() == self.second_page:
            base_dir = os.path.dirname(str(self.first_page.original_location_line_edit.text()))
            self.second_page.source_base_dir_line_edit.setText(base_dir)
        if self.currentPage() == self.third_page:
            self.third_page.form_lyt.readFromSettings()
            base_dir = str(self.third_page.form_lyt.base_dir_lineEdit.text())
            if not self.second_page.type_line_edit.isEnabled():
                asset_type = str(self.second_page.type_combo_box.currentText()).upper()
            else:
                asset_type = str(self.second_page.type_line_edit.text()).upper()
            asset_name = str(self.second_page.name_line_edit.text())
            base_dir_complete = '%s/%s/%s' % (base_dir, asset_type, asset_name)
            self.third_page.form_lyt.base_dir_lineEdit.setText(base_dir_complete)

    def clearAllFields(self):
        self.first_page.original_location_line_edit.clear()
        self.second_page.source_base_dir_line_edit.clear()
        self.second_page.type_combo_box.setCurrentIndex(0)
        self.second_page.type_line_edit.clear()
        self.second_page.name_line_edit.clear()

class AddAssetWizardPage1(QtGui.QWizardPage):
    def __init__(self, parent=None, parent_window=None):
        super(AddAssetWizardPage1, self).__init__(parent)
        self.setTitle("Browse Source File")
        self.setSubTitle('Browse to a .ma/.mb file or exported 3d file types (.fbx, .abc, .obj, .stl)')
        self.ui_widget = QtGui.QWidget()
        self.parent_window = parent_window
        self.vLyt = QtGui.QVBoxLayout(self.ui_widget)

        self.grid_lyt = QtGui.QGridLayout()

        self.original_location_line_edit = QtGui.QLineEdit(self.ui_widget)
        self.grid_lyt.addWidget(self.original_location_line_edit, 0, 0)

        browse_button = QtGui.QPushButton(self.ui_widget)
        browse_button.setText('...')
        browse_button.setMaximumSize(25, 25)
        browse_button.clicked.connect(self.openFile)
        self.grid_lyt.addWidget(browse_button, 0, 1)

        self.vLyt.addLayout(self.grid_lyt)

        spacer = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vLyt.addItem(spacer)

        self.info_label = QtGui.QLabel(self.ui_widget)
        self.info_label.setText('If you selected a Maya scene file, please wait for the file to be read upon clicking \"Next\"')
        self.vLyt.addWidget(self.info_label)

        self.lyt = QtGui.QVBoxLayout()
        self.lyt.addWidget(self.ui_widget)

        self.setLayout(self.lyt)

        self.registerField('location_line_edit*', self.original_location_line_edit, self.original_location_line_edit.text())

    def openFile(self):
        file_name, file_type = QtGui.QFileDialog.getOpenFileName(None, 'Open File', '', 'Acceptable files (*.ma *.mb *.obj *.fbx *.abc *.stl)')
        if len(file_name) > 0 and os.path.isfile(file_name):
            self.original_location_line_edit.setText(file_name)


class AddAssetWizardPage2(QtGui.QWizardPage):
    def __init__(self, parent=None, parent_window=None):
        super(AddAssetWizardPage2, self).__init__(parent)
        self.setTitle("Asset Details")
        self.setSubTitle('Add asset details')
        self.ui_widget = QtGui.QWidget()
        self.parent_window = parent_window
        self.vLyt = QtGui.QVBoxLayout(self.ui_widget)

        self.form_lyt = QtGui.QFormLayout()
        type_label = QtGui.QLabel(self.ui_widget)
        type_label.setText('Type: ')
        self.form_lyt.setWidget(0, QtGui.QFormLayout.LabelRole, type_label)

        self.type_hLyt = QtGui.QHBoxLayout(self.ui_widget)

        self.type_combo_box = QtGui.QComboBox(self.ui_widget)
        self.type_combo_box.addItem('---')
        self.type_combo_box.addItem('add new')
        self.type_combo_box.currentIndexChanged.connect(self.addNewType)
        self.type_hLyt.addWidget(self.type_combo_box)

        self.type_line_edit = QtGui.QLineEdit(self.ui_widget)
        self.type_line_edit.setEnabled(False)
        self.type_hLyt.addWidget(self.type_line_edit)

        self.form_lyt.setLayout(0, QtGui.QFormLayout.FieldRole, self.type_hLyt)

        name_label = QtGui.QLabel(self.ui_widget)
        name_label.setText('Name: ')
        self.form_lyt.setWidget(1, QtGui.QFormLayout.LabelRole, name_label)

        self.name_line_edit = QtGui.QLineEdit(self.ui_widget)
        self.form_lyt.setWidget(1, QtGui.QFormLayout.FieldRole, self.name_line_edit)

        source_base_dir_label = QtGui.QLabel(self.ui_widget)
        source_base_dir_label.setText('Base Source Directory: ')
        self.form_lyt.setWidget(2, QtGui.QFormLayout.LabelRole, source_base_dir_label)

        self.source_base_dir_line_edit = QtGui.QLineEdit(self.ui_widget)
        self.form_lyt.setWidget(2, QtGui.QFormLayout.FieldRole, self.source_base_dir_line_edit)

        self.vLyt.addLayout(self.form_lyt)

        self.lyt = QtGui.QVBoxLayout()
        self.lyt.addWidget(self.ui_widget)

        self.setLayout(self.lyt)

    def addNewType(self):
        if str(self.type_combo_box.currentText()) == 'add new':
            self.type_line_edit.setEnabled(True)
        else:
            self.type_line_edit.setEnabled(False)

class AddAssetWizardPage3(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(AddAssetWizardPage3, self).__init__(parent)
        self.setTitle("Directory Structure")
        self.setSubTitle('Set up directory structure')
        self.lyt = QtGui.QVBoxLayout()

        self.form_lyt = FolderStructureLayout()
        self.form_lyt.readFromSettings()
        self.lyt.addLayout(self.form_lyt)

        spacer1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.lyt.addItem(spacer1)

        self.button_hLyt = QtGui.QHBoxLayout()

        spacer2 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.button_hLyt.addItem(spacer2)

        self.set_defaults_btn = QtGui.QPushButton()
        self.set_defaults_btn.setText('Reset to defaults')
        self.set_defaults_btn.setMaximumWidth(100)
        self.button_hLyt.addWidget(self.set_defaults_btn)
        self.set_defaults_btn.clicked.connect(self.form_lyt.setDefaults)

        self.lyt.addLayout(self.button_hLyt)

        self.setLayout(self.lyt)

    def setButtonClicked(self):
        self.form_lyt.saveSettings()
        self.close()