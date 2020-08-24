import os
import pickle

from foreign_asset_manager.GLOBAL_VARS import DATABASE_FILE
from foreign_asset_manager.Components.AssetClass import AssetClass
from foreign_asset_manager.Components.maya_components import MayaOperationClass
from foreign_asset_manager.CustomQtObjects.TreeModel import TreeModel, DATABASE
from foreign_asset_manager.CustomQtObjects.TreeView import TreeView
from foreign_asset_manager.CustomQtObjects.Proxy01Model import Proxy01
from foreign_asset_manager.CustomQtObjects.ImageLabel import ImageLabel
from foreign_asset_manager.Windows.AddAssetWizard import Wizard
from foreign_asset_manager.Windows.PreferencesWindow import PreferencesWindow

from foreign_asset_manager import QtGui, QtCore, QT_SIGNAL, QT_SLOT

class Dialog(QtGui.QWidget):
    add_signal = QT_SIGNAL(int)

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setWindowTitle("Foreign Asset Manager")
        self.setMinimumSize(400, 175)
        self.add_wizard = Wizard()
        self.preferences_window = PreferencesWindow()
        self.maya_class = MayaOperationClass()

        self.model = TreeModel()
        self.proxy1 = Proxy01()
        self.proxy1.setSourceModel(self.model)
        self.proxy1.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy1.setDynamicSortFilter(True)

        master_lyt = QtGui.QVBoxLayout(self)
        splitter = QtGui.QSplitter(self)
        splitter.setChildrenCollapsible(False)
        splitter.setOrientation(QtCore.Qt.Horizontal)

        self.ui_widget = QtGui.QWidget(splitter)

        layout = QtGui.QVBoxLayout(self.ui_widget)
        layout.setContentsMargins(-1, 20, -1, -1)

        expand_collapse_lyt = QtGui.QHBoxLayout()
        expand_collapse_lyt.setSpacing(0)

        self.expand_all_button = QtGui.QPushButton('+')
        self.expand_all_button.setMaximumSize(20, 20)
        expand_collapse_lyt.addWidget(self.expand_all_button)

        self.collapse_all_button = QtGui.QPushButton('-')
        self.collapse_all_button.setMaximumSize(20, 20)
        expand_collapse_lyt.addWidget(self.collapse_all_button)

        spacer2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        expand_collapse_lyt.addItem(spacer2)

        self.refresh_button = QtGui.QPushButton('r')
        self.refresh_button.setMaximumSize(20, 20)
        expand_collapse_lyt.addWidget(self.refresh_button)

        layout.addLayout(expand_collapse_lyt)

        self.tree_view = TreeView()
        self.tree_view.setModel(self.proxy1)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.right_button_clicked.connect(self.rightMenuClicked)
        self.tree_view.selection_cleared.connect(self.resetPreviewImage)
        self.expand_all_button.clicked.connect(self.expandAll)
        self.collapse_all_button.clicked.connect(self.collpaseAll)
        self.refresh_button.clicked.connect(self.refreshView)
        layout.addWidget(self.tree_view)

        search_layout = QtGui.QHBoxLayout()

        self.search_line_edit = QtGui.QLineEdit()
        self.search_line_edit.setPlaceholderText('Search')
        self.search_line_edit.returnPressed.connect(self.updateFilter)
        search_layout.addWidget(self.search_line_edit)

        self.search_button = QtGui.QPushButton('Search')
        self.search_button.setMaximumWidth(75)
        self.search_button.clicked.connect(self.updateFilter)
        search_layout.addWidget(self.search_button)

        layout.addLayout(search_layout)

        QtCore.QObject.connect(self.tree_view, QtCore.SIGNAL("clicked(QModelIndex)"), self.row_clicked)
        QtCore.QObject.connect(self.tree_view, QtCore.SIGNAL("doubleClicked(QModelIndex)"), self.row_double_clicked)

        self.detail_panel_widget = QtGui.QWidget(splitter)
        image_layout = QtGui.QVBoxLayout(self.detail_panel_widget)

        self.image_label = ImageLabel(parent_view=self.tree_view)
        self.image_label.image_assign_signal.connect(self.assignImage)
        image_layout.addWidget(self.image_label)

        master_lyt.addWidget(splitter)

        self.qmenuBar = QtGui.QMenuBar(self)
        self.default_qmenubar_height = self.qmenuBar.height()
        file_menu = self.qmenuBar.addMenu('File')
        preferences_action = QtGui.QAction('Preferences', self)
        preferences_action.triggered.connect(self.preferencesClicked)
        add_asset_action = QtGui.QAction('Add new asset', self)
        add_asset_action.triggered.connect(self.addMenuClicked)
        file_menu.addAction(add_asset_action)
        file_menu.addAction(preferences_action)

    def row_clicked(self, index):
        '''
        when a row is clicked... show the name
        '''
        indexes = self.tree_view.selectedIndexes()
        if len(indexes) > 0:

            level = 0
            i = indexes[0]
            while i.parent().isValid():
                i = i.parent()
                level += 1
        if level == 2:
            index = index.parent()
        real_index = self.tree_view.model().mapToSource(index)
        asset = self.tree_view.model().sourceModel().data(real_index, QtCore.Qt.UserRole)
        if asset:
            if asset.preview_image:
                self.image_label.changeImage(asset.preview_image)
            else:
                self.resetPreviewImage()
        else:
            self.resetPreviewImage()

    def row_double_clicked(self, index):
        '''
        when a row is clicked... show the name
        '''
        real_index = self.tree_view.model().mapToSource(index)
        asset = self.tree_view.model().sourceModel().data(real_index, QtCore.Qt.UserRole)
        if asset.load_file:
            self.maya_class.openMayaFileNormally(asset.name, asset.load_file)

    def resetPreviewImage(self):
        self.image_label.resetImage()

    def assignImage(self):
        current = self.tree_view.currentIndex()
        source_index = self.proxy1.mapToSource(current)
        child_tree_item = source_index.internalPointer()
        asset = child_tree_item.asset
        new_image = self.maya_class.createThumbnail(asset.sourceimages_path)
        asset.preview_image = new_image
        self.image_label.changeImage(asset.preview_image)

    def expandAll(self):
        for row in range(self.proxy1.rowCount()):
            index = self.proxy1.index(row, 0)
            self.tree_view.expand(index)

    def collpaseAll(self):
        for row in range(self.proxy1.rowCount()):
            index = self.proxy1.index(row, 0)
            self.tree_view.collapse(index)

    def refreshView(self):
        current = self.tree_view.currentIndex()
        source_index = self.proxy1.mapToSource(current)
        self.model.refreshFileList(source_index, None)
        self.proxy1.invalidate()

    def preferencesClicked(self):
        self.preferences_window.form_lyt.readFromSettings()
        self.preferences_window.show()

    def addMenuClicked(self):
        current_combo_box_items = list()
        for i in range(int(self.add_wizard.second_page.type_combo_box.count())):
            item = self.add_wizard.second_page.type_combo_box.itemText(i)
            current_combo_box_items.append(item)
        for type in self.model.parents:
            if type == 0:
                continue
            if type not in current_combo_box_items:
                self.add_wizard.second_page.type_combo_box.addItem(type)
        self.add_wizard.clearAllFields()
        self.add_wizard.restart()
        self.add_wizard.button(QtGui.QWizard.FinishButton).clicked.connect(self.processDataToAdd)
        self.add_wizard.setWizardStyle(QtGui.QWizard.WizardStyle.ClassicStyle)
        self.add_wizard.show()

    def processDataToAdd(self):
        if not self.add_wizard.second_page.type_line_edit.isEnabled():
            asset_type = str(self.add_wizard.second_page.type_combo_box.currentText()).upper()
        else:
            asset_type = str(self.add_wizard.second_page.type_line_edit.text()).upper()
        name = str(self.add_wizard.second_page.name_line_edit.text())
        source_path = str(self.add_wizard.first_page.original_location_line_edit.text())
        source_dir_path = os.path.dirname(source_path)
        source_base_path = str(self.add_wizard.second_page.source_base_dir_line_edit.text())
        if source_base_path.endswith('/'):
            source_base_path = source_base_path[:-1]
        location = str(self.add_wizard.third_page.form_lyt.base_dir_lineEdit.text())
        scenes_dirname = str(self.add_wizard.third_page.form_lyt.scene_lineEdit.text())
        textures_dirname = str(self.add_wizard.third_page.form_lyt.textures_lineEdit.text())
        sourceimages_dirname = str(self.add_wizard.third_page.form_lyt.sourceimages_lineEdit.text())
        references_dirname = str(self.add_wizard.third_page.form_lyt.references_lineEdit.text())
        cache_dirname = str(self.add_wizard.third_page.form_lyt.cache_lineEdit.text())
        renders_dirname = str(self.add_wizard.third_page.form_lyt.renders_lineEdit.text())
        asset = AssetClass(type=asset_type,
                           name=name,
                           date_added=QtCore.QDateTime.currentDateTime(),
                           source_file=source_path,
                           source_dir=source_dir_path,
                           source_base_dir=source_base_path,
                           dir=location,
                           scenes=scenes_dirname,
                           textures=textures_dirname,
                           sourceimages=sourceimages_dirname,
                           references=references_dirname,
                           cache=cache_dirname,
                           renders=renders_dirname)
        self.maya_class.buildProject(asset)
        self.model.addSubRow(asset)
        self.proxy1.invalidate()

    @QT_SLOT(str)
    def rightMenuClicked(self, mode):
        if mode == 'delete':
            self.deleteButtonClicked()
        elif mode == 'explorer':
            self.explorerMenuClicked()
            # print 'open in explorer'

    def explorerMenuClicked(self):
        current = self.tree_view.currentIndex()
        source_index = self.proxy1.mapToSource(current)
        self.model.openInExplorer(source_index)

    def deleteButtonClicked(self):
        current = self.tree_view.currentIndex()
        source_index = self.proxy1.mapToSource(current)
        self.model.customRemoveRow(source_index)
        self.proxy1.invalidate()

    def updateFilter(self):
        text = str(self.search_line_edit.text())
        rows_to_expand = list()
        row_count = self.proxy1.rowCount()
        for row in range(row_count):
            index = self.proxy1.index(row, 0)
            if self.tree_view.isExpanded(index):
                rows_to_expand.append(index)
        print rows_to_expand
        self.proxy1.setFilterRegExp(text)
        for row in range(row_count):
            index = self.proxy1.index(row, 0)
            if index in rows_to_expand:
                self.tree_view.expand(index)
            else:
                self.tree_view.collapse(index)

    def resizeEvent(self, event):
        super(Dialog, self).resizeEvent(event)
        self.qmenuBar.resize(self.width(), self.default_qmenubar_height * 0.75)

    def saveDatabase(self):
        row_count = self.proxy1.rowCount()
        # for row in range(row_count):
        #     index = self.proxy1.index(row, 0)
        #     source_index = self.proxy1.mapToSource(index)
        #     parent_tree_item = source_index.internalPointer()
        #     for child_item in parent_tree_item.child_items:
        #         if child_item.asset.key_str in DATABASE:
        #             continue
        #         DATABASE[child_item.asset.key_str] = child_item.asset
        # with open(DATABASE_FILE, 'wb') as output:
        #     pickle.dump(DATABASE, output)
        # print 'successfully saved database'

    def closeEvent(self, event):
        self.saveDatabase()
        super(Dialog, self).closeEvent(event)