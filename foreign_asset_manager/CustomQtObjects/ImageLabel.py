from foreign_asset_manager import QtGui, QtCore, QT_SIGNAL

class ImageLabel(QtGui.QLabel):
    image_assign_signal = QT_SIGNAL()

    def __init__(self, parent=None, image_path=None, parent_view=None):
        super(ImageLabel, self).__init__(parent)
        self.setMinimumSize(50, 50)
        self.default_image = "D:/PC6/Pictures/no_image_found_icon.jpg"
        self.parent_view = parent_view
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        width = 100
        height = 100
        self.pic = QtGui.QPixmap()
        self.pic.load(self.default_image)
        self.setPixmap(self.pic.scaled(width, height, QtCore.Qt.KeepAspectRatio))

    def openMenu(self, position):
        if not self.parent_view:
            return
        indexes = self.parent_view.selectedIndexes()
        if not indexes:
            return
        if len(indexes) > 0:

            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QtGui.QMenu()
        assign_new_image_action = None

        if level == 1:
            assign_new_image_action = QtGui.QAction('Assign new thumbnail from viewport', self)
            menu.addAction(assign_new_image_action)

        if assign_new_image_action:
            assign_new_image_action.triggered.connect(self._on_click)

        menu.exec_(self.mapToGlobal(position))

    def _on_click(self):
        self.image_assign_signal.emit()

    def resetImage(self):
        self.changeImage(self.default_image)

    def changeImage(self, new_image_path):
        self.pic.load(new_image_path)
        width = self.width()
        height = self.height()
        self.setPixmap(self.pic.scaled(width, height, QtCore.Qt.KeepAspectRatio))

    def resizeEvent(self, event):
        super(ImageLabel, self).resizeEvent(event)
        width = self.width()
        height = self.height()
        self.setPixmap(self.pic.scaled(width, height, QtCore.Qt.KeepAspectRatio))