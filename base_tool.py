import argparse 

from filesystem import FSGetter


class BaseTool(object):

    def __init__(self):
        self._fs_getter = FSGetter()


    def _parse_args(self, args_list=None):

        parser = argparse.ArgumentParser()
        self._add_common_args(parser)
        self._add_extra_args(parser)

        args = parser.parse_args(args_list)
        self._set_units_default(args)

        self._args = args


    def _add_extra_args(self, parser):
        pass


    def _add_common_args(self, parser):

        "add arguments that are used both by the df and du utilities"

        size_disp = parser.add_mutually_exclusive_group()

        size_disp.add_argument('--units', '-u', 
                               choices=['T', 'Ti', 'G', 'Gi', 'M', 'Mi', 'k', 'ki',
                                        'B'],
                               help=('Units to display sizes, where: '
                                     'T = 1000^4 bytes,'
                                     'G = 1000^3 bytes,'
                                     'M = 1000^2 bytes,'
                                     'k = 1000 bytes,'
                                     'B = bytes,'
                                     'Ti = 1024^4 bytes,'
                                     'Gi = 1024^3 bytes,'
                                     'Mi = 1024^2 bytes,'
                                     'ki = 1024 bytes.'))

        size_disp.add_argument('--decimal', '-d',
                               action='store_true',
                               help=('Display sizes human-readably in decimal units '
                                     '(choose unit so that values are in range 1.0 to 999 '
                                     'and also show the unit). This is the default.'))

        size_disp.add_argument('--binary', '-b',
                               action='store_true',
                               help='Analogous to -d, but with powers of 1024')

        parser.add_argument('--json', '-j', action='store_true',
                            help='Write output in JSON format')


    def _set_units_default(self, args):
        if args.units == None and args.decimal == False and args.binary == False:
            args.decimal = True
