import logging
import re
import numpy as np
from .. import _setup_cfg

_logger = logging.getLogger('Innate')


def generate_specific_function(expression, coefficients, variable_names):
    # Define the function to only vary with specified variables
    def specific_function(*variable_values):
        local_vars = coefficients.copy()  # Copy the dictionary of fixed variables
        # Update variable names with values dynamically from the input
        local_vars.update(dict(zip(variable_names, variable_values)))
        local_vars['np'] = np  # Ensure np is available for np.log10 and other operations
        return eval(expression, {}, local_vars)
    # The number of inputs is now the number of variable names provided
    return np.frompyfunc(specific_function, len(variable_names), 1)


def extract_coef_names(expression):
    # Regex to find isolated letters (considered variables)
    pattern = r'\b[a-zA-Z]\b'
    # Find all matches and return as a set to remove duplicates
    matches = set(re.findall(pattern, expression))
    return sorted(matches)


def create_coef_dict (coef_names, coef_values):
    if len(coef_names)==len(coef_values):
       out = dict(zip(coef_names, coef_values))
    else:
        raise TypeError("length of coefficietns names different from the length of coefficients values")
    return(out)


def extract_variables_names(expression, suffix='_range'):
    # Construct the regex pattern dynamically to find words ending with the given suffix
    pattern = rf'\b\w+{re.escape(suffix)}\b'  # Use re.escape to safely include the suffix in the regex
    # Find all matches and return as a set to remove duplicates
    matches = set(re.findall(pattern, expression))
    return sorted(list(matches))  # Return a sorted list of unique matches


def parse_string_equation(data_label, str_eqn, coeffs_eqn, variable_names):

    if (str_eqn is not None) or (coeffs_eqn is not None):
        coef_names = extract_coef_names(str_eqn)
        coeffs_dict = create_coef_dict(coef_names, coeffs_eqn)
        eqn = generate_specific_function(str_eqn, coeffs_dict, variable_names)

    else:
        message = f'Data set "{data_label}" is missing:'
        if str_eqn is None:
            message += f'\nParametrisation formula ("eqn" key in dataset configuration).'
        if coeffs_eqn is None:
            message += f'\nParametrisation coefficients ("eqn_coeffs" key in dataset configuration).'
        _logger.warning(message)

        eqn, coeffs_dict = None, None

    return eqn, coeffs_dict


class Regressor:

    def __init__(self, grid, technique_list, data_cfg=None):

        self.eqn = None
        self.coeffs = None
        self.techniques = []

        # Constrain to regresion techniques
        algorithms = list(set(_setup_cfg['parameter_labels']['reg'].keys()) & set(technique_list))

        # Regular grid Interpolation
        if 'eqn' in algorithms:
            self.techniques.append('eqn')

            # Reconstruct the string equation into a python function
            self.eqn, self.coeffs = parse_string_equation(grid.label,
                                                          data_cfg.get('eqn', None),
                                                          data_cfg.get('eqn_coeffs', None),
                                                          data_cfg.get('axes', None))

        return




