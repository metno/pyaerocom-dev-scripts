#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 12:32:50 2020

@author: jonasg
"""


import abc
from pyaerocom.mathutils import compute_angstrom_coeff_cubes

class ReadGriddedBase(abc.ABC):
    # template base class (the API defined here would need to be implemented in gridded readers
    # and the factory class `ReadGridded` could make use of that.
    # common attributes and method declararions, e.g.

    AUX_REQUIRES = {'ang4487aer'    : ('od440aer', 'od870aer'),}
    AUX_FUNS = {'ang4487aer'   :    compute_angstrom_coeff_cubes}

    @property
    @abc.abstractmethod
    def data_id(self):
        # data ID
        pass

    @property
    @abc.abstractmethod
    def data_dir(self):
        # data ID
        pass

    @abc.abstractmethod
    def has_var(self, var_name):
        # Declared (needs to be implemented returns boolean
        pass

    @abc.abstractmethod
    def read_var(self, var_name, *args,  **kwargs):
        # returns GriddedData
        pass

class ReadGriddedAerocom(ReadGriddedBase):
    # currently called `ReadGridded` and implemented in readgridded.py (master)
    pass

class ReadGriddedEmep(ReadGriddedBase):
    # currently called ReadEMEP and implemented by @ejgal (branch ReadEMEP)
    pass

class ReadGridded(object):
    # factory that has all implementations of ReadGriddedBase registered
    SUPPORTED = [ReadGriddedAerocom, ReadGriddedEmep]

    def __init__(self, data_id, data_dir, **ini_opts):
        self.data_id = data_id
        self.data_dir = data_dir

        self._ini_opts = {}
        self._ini_opts.update(ini_opts)

    def get_reader(self):
        """
        Identify reader based on data_id

        ToDo: missing logic that needs to be implemented. Needs to be disscussed
        how to do that best.

        Returns
        -------
        ReadGriddedBase
            reader class derived from :class:`ReadGriddedBase`
        """
        raise NotImplementedError

    def read_var(self, var_name, **kwargs):
        """
        Read gridded variable data

        Parameters
        ----------
        var_name : str
            Name of variable that is supposed to be read.
        **kwargs : TYPE
            additional keyword agrs parsed to :func:`read_var` of reader
            class.

        Returns
        -------
        GriddedData
            Loaded data object

        """
        reader_cls = self.get_reader()
        # init reader
        reader = reader_cls(data_id=self.data_id,
                            data_dir=self.data_dir,
                            **self._ini_opts)

        return reader.read_var(var_name, **kwargs)

if __name__ == '__main__':

    reader = ReadGridded('NorESM2-met2010_AP3-CTRL')

    aerocom_data = reader.read_var('od550aer')

    reader = ReadGridded('EMEP-testrun',
                         data_dir='/home/my_emep_output')

    emep_data = reader.read_var('vmro3')
