import sys
import os
import pickle

from foreign_asset_manager.GLOBAL_VARS import HORIZONTAL_HEADERS, DATABASE_FILE, ACCEPTABLE_FILE_TYPES
from foreign_asset_manager.Components.AssetClass import AssetClass
sys.modules['__main__'].AssetClass = AssetClass
from foreign_asset_manager.CustomQtObjects.TreeItem import TreeItem

from foreign_asset_manager import QtCore

if os.path.isfile(DATABASE_FILE):
    with open(DATABASE_FILE, 'rb') as input:
        DATABASE = pickle.load(input)
else:
    DATABASE = dict()

print DATABASE

class TreeModel(QtCore.QAbstractItemModel):
    '''
    a model to display a few names, ordered by sex
    '''

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self.assets = []
        for asset_key, asset in DATABASE.iteritems():
            self.assets.append(asset)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0: self.rootItem}
        self.setupModelData()

    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return None


        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.asset

        return None

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
                role == QtCore.Qt.DisplayRole):
            try:
                return HORIZONTAL_HEADERS[column]
            except IndexError:
                pass
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        childItem = parent_item.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()

        parent_item = childItem.parent()

        if parent_item == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()

    def setupModelData(self):
        for asset in self.assets:
            asset_type = asset.type

            if not self.parents.has_key(asset_type):
                new_parent = TreeItem(None, asset_type, self.rootItem)
                self.rootItem.appendChild(new_parent)

                self.parents[asset_type] = new_parent

            parent_item = self.parents[asset_type]
            new_item = TreeItem(asset, "", parent_item)
            parent_item.appendChild(new_item)
            self.refreshFileList(None, new_item)

    def addSubRow(self, asset):
        asset_type = asset.type
        name = asset.name
        if not self.parents.has_key(asset_type):
            new_parent = TreeItem(None, asset_type, self.rootItem)
            self.rootItem.appendChild(new_parent)

            self.parents[asset_type] = new_parent
        parent_item = self.parents[asset_type]
        already_exists = False
        for child in parent_item.child_items:
            if child.asset.name == name and child.asset.type == asset_type:
                already_exists = True
        if already_exists:
            print 'this asset already exists'
            return
        new_item = TreeItem(asset, "", parent_item)
        parent_item.appendChild(new_item)
        self.refreshFileList(None, new_item)

    def customRemoveRow(self, rowIndex):
        child_tree_item = rowIndex.internalPointer()
        asset_type = rowIndex.parent().data()
        parent_item = self.parents[str(asset_type)]
        self.beginRemoveRows(rowIndex.parent(), rowIndex.row(), rowIndex.row() + 1)
        parent_item.removeChild(child_tree_item)
        self.endRemoveRows()

    def refreshFileList(self, rowIndex, child_item):
        if rowIndex:
            child_tree_item = rowIndex.internalPointer()
        else:
            child_tree_item = child_item
        if child_tree_item.asset and child_tree_item.asset.source_dir:
            file_dir_path = child_tree_item.asset.scenes_path
            date_to_files_dict = dict()
            for file in os.listdir(file_dir_path):
                extension = file.rpartition('.')[2]
                if extension not in ACCEPTABLE_FILE_TYPES:
                    continue
                file_path = '%s/%s' % (file_dir_path, file)
                if os.path.isdir(file_path):
                    continue
                modified_time = int(os.path.getmtime(file_path))
                print modified_time
                file_asset_obj = AssetClass(name=file,
                                            date_file_modified=QtCore.QDateTime.fromTime_t(modified_time),
                                            date_timestamp=modified_time,
                                            load_file=file_path)
                date_to_files_dict[modified_time] = file_path
                new_treeItem_obj = TreeItem(file_asset_obj, '', child_tree_item)
                child_tree_item.appendChild(new_treeItem_obj)
            child_tree_item.asset.load_file = date_to_files_dict[max(date_to_files_dict)]

    def openInExplorer(self, rowIndex):
        child_tree_item = rowIndex.internalPointer()
        os.startfile(child_tree_item.asset.scenes_path)