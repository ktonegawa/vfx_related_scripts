from foreign_asset_manager.CustomQtObjects.FolderStructureLayout import FolderStructureLayout

from foreign_asset_manager import QtGui

class PreferencesWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PreferencesWindow, self).__init__(parent)
        self.setWindowTitle('Preferences')
        self.resize(425, 250)
        self.lyt = QtGui.QVBoxLayout()

        self.direction_label = QtGui.QLabel()
        self.direction_label.setText('Set the default path and folder names of elements')
        direction_font = QtGui.QFont()
        direction_font.setPointSize(12)
        self.direction_label.setFont(direction_font)
        self.lyt.addWidget(self.direction_label)

        self.form_lyt = FolderStructureLayout()
        self.lyt.addLayout(self.form_lyt)

        self.button_hLyt = QtGui.QHBoxLayout()

        self.set_pref_btn = QtGui.QPushButton()
        self.set_pref_btn.setText('Set')
        self.set_pref_btn.clicked.connect(self.setButtonClicked)
        self.button_hLyt.addWidget(self.set_pref_btn)

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