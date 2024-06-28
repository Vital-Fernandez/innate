import innate
import numpy as np
import pyneb as pn

data_file = '../data/emissivity_grids.nc'
emissivities = innate.DataSet.from_file(data_file)

# Additional approximation techniques can be accessed from the interpolation (interpl) and regression
# (reg) objects as provided by the input dataset file. For example, the current dataset includes a parametrization for the
# 2D grids:

emissivities['O3_5007A'].approx.reg.eqn(12250, 122)

# Which produces the same results as above.
# In 2D datasets it is possible to perform these validations with a visual approach using the plottting function:

emissivities['O3_5007A'].plot.matrix_diagnostic(ax_cfg={'title': '$O^{2+} 500.7nm$'})

# We can compare this plot with another transitions

emissivities['He1_7065A'].plot.matrix_diagnostic(ax_cfg={'title': '$He^{+} 706.5nm$'})

# We can see the second set of emissivities have high discrepancy at high density  low temperature. This means we should
# review the approximation technique if these conditions are found.


# menu. from the programing manner.
temp, den = 12250, 122
print('Regression Equation', emissivities['O3_5007A'].approx.reg.eqn(12250, 122))


