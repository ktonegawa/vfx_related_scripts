class AssetClass(object):
    '''
    a trivial custom data object
    '''

    def __init__(self, **kwargs):
        if not kwargs.get('name'):
            return
        self.name = kwargs.get('name')
        self.date_added = kwargs.get('date_added')
        self.date_file_modified = kwargs.get('date_file_modified')
        self.date_timestamp = kwargs.get('date_timestamp')
        self.type = kwargs.get('type')
        self.source_file = kwargs.get('source_file')
        self.source_dir = kwargs.get('source_dir')
        self.source_base_dir = kwargs.get('source_base_dir')
        self.dir = kwargs.get('dir')
        self.load_file = kwargs.get('load_file')
        self.scenes_dir = kwargs.get('scenes')
        self.textures_dir = kwargs.get('textures')
        self.sourceimages_dir = kwargs.get('sourceimages')
        self.references_dir = kwargs.get('references')
        self.cache_dir = kwargs.get('cache')
        self.renders_dir = kwargs.get('renders')
        self.preview_image = kwargs.get('preview_image')

    @property
    def scenes_path(self):
        return '%s/%s' % (self.dir, self.scenes_dir)

    @property
    def textures_path(self):
        return '%s/%s' % (self.dir, self.textures_dir)

    @property
    def sourceimages_path(self):
        return '%s/%s' % (self.dir, self.sourceimages_dir)

    @property
    def references_path(self):
        return '%s/%s' % (self.dir, self.references_dir)

    @property
    def cache_path(self):
        return '%s/%s' % (self.dir, self.cache_dir)

    @property
    def renders_path(self):
        return '%s/%s' % (self.dir, self.renders_dir)

    @property
    def key_str(self):
        return "%s - %s" % (self.type, self.name)

    def __repr__(self):
        return "%s - %s %s" % (self.type, self.name, self.date_added)

