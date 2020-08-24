import sys

from foreign_asset_manager.Windows.Dialog import Dialog

# LOADED_QT_VERSION = None
#
# try:
#     from PySide import QtGui
#     LOADED_QT_VERSION = 'PySide'
# except ImportError:
#     from PyQt4 import QtGui
#     LOADED_QT_VERSION = 'PyQt4'
#
# def run():
#     dialog = Dialog()
#     dialog.show()

from foreign_asset_manager import QtGui

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(app.exec_())