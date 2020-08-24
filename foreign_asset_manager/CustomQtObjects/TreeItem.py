from foreign_asset_manager.GLOBAL_VARS import HORIZONTAL_HEADERS

class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''

    def __init__(self, asset, header, parent_item):
        self.asset = asset
        self.parent_item = parent_item
        self.header = header
        self.child_items = []

    def appendChild(self, item):
        self.child_items.append(item)

    def removeChild(self, item):
        self.child_items.remove(item)

    def child(self, row):
        return self.child_items[row]

    def childCount(self):
        return len(self.child_items)

    def columnCount(self):
        return len(HORIZONTAL_HEADERS)

    def data(self, column):
        if self.asset == None:
            if column == 0:
                return self.header
            if column == 1:
                return None
        else:
            if column == 0:
                return self.asset.name
            if column == 1:
                return self.asset.date_added
            if column == 2:
                return self.asset.dir
            if column == 4:
                return self.asset.date_file_modified
        return None

    def parent(self):
        return self.parent_item

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0