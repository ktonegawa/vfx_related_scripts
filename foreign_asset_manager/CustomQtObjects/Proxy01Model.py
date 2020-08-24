from foreign_asset_manager import QtGui, QtCore

class Proxy01(QtGui.QSortFilterProxyModel):
    def __init__(self):
        super(Proxy01, self).__init__()
        self.keyword = None
        self.searched_parents = None

    def setFilterRegExp(self, pattern):
        if isinstance(pattern, str):
            pattern = QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive,
                                        QtCore.QRegExp.FixedString)
        super(Proxy01, self).setFilterRegExp(pattern)

    def _accept_index(self, idx):
        if idx.isValid():
            model = idx.model()
            if model.data(idx, QtCore.Qt.UserRole):
                text = idx.model().data(idx, QtCore.Qt.UserRole).__repr__()
            else:
                text = idx.data(QtCore.Qt.DisplayRole)
            if self.filterRegExp().indexIn(text) >= 0:
                return True
            for row in range(idx.model().rowCount(idx)):
                if self._accept_index(idx.model().index(row, 0, idx)):
                    return True
        return False

    def filterAcceptsRow(self, source_row, source_parent):
        idx = self.sourceModel().index(source_row, 0, source_parent)
        return self._accept_index(idx)