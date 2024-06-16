import innate
import lime
from innate.io import h5netcdf_file_load
import pyneb as pn

data_file = '../data/emissivity_grids.nc'
emissivities = innate.DataSet.from_file(data_file)

temp, den = 12250, 122
print('Interpolation', emissivities['O3_5007A'].approx.interp.rgi((temp, den)).eval())

# Compare with the original data
O3, H1 = pn.Atom('O', 3), pn.RecAtom('H', 1)
emiss_ratio = O3.getEmissivity(temp, den, wave=5007)/H1.getEmissivity(temp, den, wave=4861)
print('True value', emiss_ratio)

