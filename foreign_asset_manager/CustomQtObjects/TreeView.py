from functools import partial

from foreign_asset_manager import QtGui, QtCore, QT_SIGNAL

class TreeView(QtGui.QTreeView):
    right_button_clicked = QT_SIGNAL(str)
    selection_cleared = QT_SIGNAL()

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def selectedRows(self):
        rows = []
        for index in self.selectedIndexes():
            if index.column() == 0:
                rows.append(index.row())
        return rows

    def openMenu(self, position):
        indexes = self.selectedIndexes()
        if len(indexes) > 0:

            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QtGui.QMenu()
        delete_menu = None
        open_explorer_menu = None

        if level == 1:
            open_explorer_menu = QtGui.QAction("Open in Explorer", self)
            menu.addAction(open_explorer_menu)
            delete_menu = QtGui.QAction("Delete", self)
            menu.addAction(delete_menu)

        if open_explorer_menu:
            open_explorer_menu.triggered.connect(partial(self._on_right_click, 'explorer'))

        if delete_menu:
            delete_menu.triggered.connect(partial(self._on_right_click, 'delete'))

        menu.exec_(self.viewport().mapToGlobal(position))

    def _on_right_click(self, mode):
        self.right_button_clicked.emit(mode)

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self.selectionModel().clear()
            self.selection_cleared.emit()
        QtGui.QTreeView.mousePressEvent(self, event)