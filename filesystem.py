import os
import re


class UnrecognisedFSType(Exception):
    pass


class Filesystem(object):

    name = 'Generic'

    def __init__(self, mount_point, fs_spec=None, comments=''):
        self.mount_point = mount_point
        self.fs_spec = fs_spec
        self.comments = comments
        self._statvfs_data = None


    @property
    def _statvfs(self):
        if self._statvfs_data == None:
            self._statvfs_data = os.statvfs(self.mount_point)
        return self._statvfs_data


    def get_free_bytes(self):
        fss = self._statvfs
        return fss.f_bfree * fss.f_bsize


    def get_total_bytes(self):
        fss = self._statvfs
        return fss.f_blocks * fss.f_bsize


    def get_used_bytes(self):
        return self.get_total_bytes() - self.get_free_bytes()


    def _get_dirent_bytes(self, path):
        s = os.lstat(path)
        return s.st_blocks * 512


    def get_directory_bytes(self, path):
        total = 0
        for root, dirs, files in os.walk(path):
            for relpath in dirs + files:
                dirent = os.path.join(root, relpath)
                total += self._get_dirent_bytes(dirent)
        return total


class LocalFS(Filesystem):
    name = 'Local filesystem'


class PanasasFS(Filesystem):
    name = 'Panasas'


class PureFS(Filesystem):
    name = 'PURE'


class QuoByteFS(Filesystem):
    name = 'QuoByte'



class FSGetter(object):

    
    _fs_classes = {'panfs': PanasasFS,
                   'pure': PureFS,
                   'qb': QuoByteFS,
                   'local': LocalFS}


    def __init__(self, config_file=None):

        self._fs_matchers = []
        self._mount_points = {}

        if config_file == None:
            config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       'config.txt')

        self._read_config(config_file)
        self._read_mounts()


    def _strip_trailing_slash(self, dirname):
        while dirname.endswith('/') and len(dirname) > 1:
            dirname = dirname[:-1]
        return dirname


    def _read_mounts(self):
        with open('/proc/mounts') as f:
            for line in f:
                bits = line.split()
                fs_spec = bits[0]
                mount_point = bits[1]
                mount_point = self._strip_trailing_slash(mount_point)  # paranoia
                self._mount_points[mount_point] = fs_spec
        assert('/' in self._mount_points)


    def _read_config(self, config_file):
        with open(config_file) as f:
            tokeniser = re.compile('([^:]+):([^:]*):(.*)$').match
            for line in f:                
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                m = tokeniser(line)
                if not(m):
                    raise Exception("bad line in config file: {}".format(line))

                fs_type = m.group(1)
                comments = m.group(2)
                regexp = m.group(3) + '$'                

                if fs_type not in self._fs_classes:
                    raise Exception("bad line in config file: '{}': '{}' undefined fs code"
                                    .format(line, fs_type))

                matcher = re.compile(regexp)
                fs_class = self._fs_classes[fs_type]

                self._fs_matchers.append((matcher, fs_class, comments))


    def _get_mount_point(self, path):
        "Get mount point corresponding to a path, returns 2-tuple (mount point, fs_spec)"

        realpath = os.path.realpath(path) 
        realpath = self._strip_trailing_slash(realpath)  # paranoia

        # ascend directory elements until we find a known mount point
        while True:
            if realpath in self._mount_points:
                return realpath, self._mount_points[realpath]

            # should not have got to root dir without finding something
            assert(realpath != '/')

            realpath = os.path.dirname(realpath)
            
        # should not be reached
        assert(False)


    def _get_fs_class_and_comments(self, mount_point):
        for matcher, cls, comments in self._fs_matchers:
            if matcher.match(mount_point):
                return cls, comments
        raise UnrecognisedFSType(mount_point)


    def _get_fs_comments(self, mount_point):
        try:
            cls, comments = self._get_fs_class_and_comments(mount_point)
            return comments
        except UnrecognisedFSType:
            return ''
    

    def get_fs_obj(self, path, allow_unrecognised=False):

        "Get a Filesystem object corresponding to a particular path"
        mount_point, fs_spec = self._get_mount_point(path)

        # get filesystem class - if it is obvious from /proc/mounts then use that, 
        # and only use the lookup table to fetch any comments, 
        # otherwise fully use our lookup table

        if fs_spec.startswith("panfs://"):
            fs_cls = PanasasFS
            comments = self._get_fs_comments(mount_point)
        elif fs_spec.startswith("quobyte@"):
            fs_cls = QuoByteFS
            comments = self._get_fs_comments(mount_point)
        else:
            try:
                fs_cls, comments = self._get_fs_class_and_comments(mount_point)
            except UnrecognisedFSType:
                if allow_unrecognised:
                    print("WARNING: filesystem type for {} unrecognised; using generic fs type"
                          .format(mount_point))
                    fs_cls = Filesystem
                else:
                    raise
        return fs_cls(mount_point, fs_spec=fs_spec, comments=comments)
    

    def get_all_filesystems(self):
        fss = []
        for mount_point in self._mount_points:
           try:
               fss.append(self.get_fs_obj(mount_point))
           except UnrecognisedFSType:
               pass
        return fss



if __name__ == '__main__':

    fsg = FSGetter()
    fs = fsg.get_fs_obj("/tmp/mydir")

    print(fs.get_used_bytes() / 1024**3, "GB used")
    print(fs.get_directory_bytes("/tmp/mydir/dir")) 
    print(fs.get_directory_bytes("/tmp/mydir")) 
