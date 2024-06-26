import numpy as np
import re


#workflow
# 1) a)  pass expression 


#expect that numpy is imported as np
#expression the formula you want to get the corresponding function
#coefficients a dictionnary: keys are the coefficients name in the expression an values are your values
#variable names the names of the variable you want to evaluate this function on
=======

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
    else :
        raise TypeError("length of coefficietns names different from the length of coefficients values")
    return(out)

=======

def extract_variables_names(expression, suffix='_range'):
    # Construct the regex pattern dynamically to find words ending with the given suffix
    pattern = rf'\b\w+{re.escape(suffix)}\b'  # Use re.escape to safely include the suffix in the regex
    # Find all matches and return as a set to remove duplicates
    matches = set(re.findall(pattern, expression))
    return sorted(list(matches))  # Return a sorted list of unique matches
