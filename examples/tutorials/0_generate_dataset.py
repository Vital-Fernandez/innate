import numpy as np
import lime
import innate
import pyneb as pn


# Create a database with atomic transition emissivity grids
lines_db = lime.line_bands((3000, 10000))
lines_db['norm_line'] = 'H1_4861A'
lines_db = lines_db.drop(['H1_4861A', 'Fe3_4658A'])

# Compute the ranges:
temp_range = np.linspace(9000, 20000, 251)
den_range = np.linspace(1, 600, 101)

# Normalization for the emissivities
H1 = pn.RecAtom('H', 1)
norm_emiss = H1.getEmissivity(temp_range, den_range, wave=4861.0)

# Container output grids
atom_dict, emiss_dict = {}, {}

# Loop through the lines and compute the emissivities
wavelength, particle, t_type = lines_db[['wavelength', 'particle', 'transition']].to_numpy().T
for i, line_name in enumerate(lines_db.index):

    # Get transition atom pyneb object
    print(f'-- {line_name}')
    elem, ionization = particle[i][:-1], particle[i][-1]
    atom = pn.RecAtom(elem, ionization) if t_type[i] == 'rec' else pn.Atom(elem, ionization)

    # Compute and normalize the emissivities
    grid_i = atom.getEmissivity(temp_range, den_range, wave=np.round(wavelength[i]))
    emiss_dict[line_name] = grid_i/norm_emiss

# Data attributes
data_conf = {'parameter': 'emissivity', 'approximation': ('rgi', 'eqn'), 'axes': ('temp', 'den'),
             'temp_range': (9000, 20000, 251), 'den_range': (1, 600, 101)}
trans_conf = {'H1_6563A': {'eqn': 'y~2.3x + 4.3x**2 + 6.3x**3'}}

# Save the data into a dictionary
output_file = f'../data/emissivity_grids.nc'
innate.save_dataset(output_file, emiss_dict, data_conf, trans_conf)
