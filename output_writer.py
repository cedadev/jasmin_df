import math


class SizeFormatter(object):

    _units = {1000: [ 'B', 'k', 'M', 'G', 'T', 'P' ],
              1024: [ 'B', 'ki', 'Mi', 'Gi', 'Ti', 'Pi' ]}


    def __init__(self,
                 units=None, 
                 hr_decimal=False,
                 hr_binary=False):

        """
        Size formatter. Instantiate with e.g. units='k',
        or pass hr_decimal=True for human-readable numbers using powers of 1000
        or pass hr_binary=True for human-readable numbers using powers of 1024
        """
        
        if int(units != None) + int(bool(hr_decimal)) + int(bool(hr_binary)) != 1:
            raise ValueError("exactly one of 'units' or 'hr_decimal' or 'hr_binary' needed")

        if hr_decimal:
            self._hr = True
            self._mult = 1000
        
        elif hr_binary:
            self._hr = True
            self._mult = 1024

        else:
            self._hr = False
            self._unit = units            
            self._power, self._mult, value = self._lookup_unit(units)
            self._unit_value = float(value)
            

    def _lookup_unit(self, unit):

        for mult in 1000, 1024:
            known_units = self._units[mult]
            if unit in known_units:
                power = known_units.index(unit)
                value = mult ** power
                return power, mult, value
        else:
            raise ValueError("unknown unit '{}'".format(unit))


    def describe_units(self):
        if self._hr:
            return "powers of {} bytes".format(self._mult)
        elif self._power == 0:
            return 'bytes'
        else:
            if self._power == 1:
                powerdesc = ""
            else:
                powerdesc = " ^ {}".format(self._power)
            return("{} ({}{} bytes)".format(self._unit,
                                            self._mult,
                                            powerdesc))
                                            


    def format_size(self, bytes, with_units=False):

        """
        format size in bytes into specific number, depending on units in use;
        returns string

        if with_units==True then include the units in the output; otherwise only do so if 
        human-readable was specified and bytes is non-zero
        """

        if not isinstance(bytes, int):
            raise ValueError('bytes must be specified as integer')

        if self._hr:
            if bytes == 0: return '0'

            power = 0
            value = float(bytes)
            while value >= self._mult:
                power += 1
                value /= self._mult

            unit = self._units[self._mult][power]

            if value < 10 and power > 0:
                return '{:.1f}{}'.format(value, unit)
            else:
                return '{:.0f}{}'.format(value, unit)
        
        else:
            val = str(math.ceil(bytes / self._unit_value))
            if with_units:
                val += ' ' + self._unit
            return val


if __name__ == '__main__':
    
    formatters = [SizeFormatter(hr_decimal=True),
                  SizeFormatter(hr_binary=True),
                  SizeFormatter(units='Mi'),
                  SizeFormatter(units='k'),
                  SizeFormatter(units='G')]

    f = '{:24s}'.format

    print(f('Units'),
          ''.join([f(formatter.describe_units()) 
                   for formatter in formatters]))

    val = 1
    while(val < 1e13):
        val *= 3
        print(f(str(val)),
              ''.join([f(formatter.format_size(val))
                       for formatter in formatters]))
