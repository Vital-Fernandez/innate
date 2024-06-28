import innate
import pyneb as pn
import numpy as np

data_file = '../data/emissivity_grids.nc'
emissivities = innate.DataSet.from_file(data_file)

input_line = 'H1_6563A'
grid = emissivities[input_line]
grid.plot.matrix_diagnostic()
