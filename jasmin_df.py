from base_tool import BaseTool


class DF(BaseTool):


    def _add_extra_args(self, parser):
        parser.add_argument('directory', type=str, metavar='path', 
                            nargs='*')

    def _get_space(self, fs):
        used, total = (fs.get_used_bytes(),
                       fs.get_total_bytes())
        avail = total - used
        try:
            percent = 100. * used / total
        except ZeroDivisionError:
            percent = 0.
        return fs.name, fs.comments, fs.fs_spec, total, used, avail, percent, fs.mount_point
    

    def run(self):
        self._parse_args()
        if self._args.directory:
            for path in self._args.directory:
                fs = self._fs_getter.get_fs_obj(path, allow_unrecognised=True)
                print(self._get_space(fs))
        else:
            for fs in self._fs_getter.get_all_filesystems():
                print(self._get_space(fs))                

                      


def main():
    df = DF()
    df.run()


if __name__ == '__main__':
    
    main()
