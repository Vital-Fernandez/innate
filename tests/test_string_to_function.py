import numpy as np
import pytest
 
from innate.regression.methods import generate_specific_function  
from innate.regression.methods import extract_coef_names  
from innate.regression.methods import extract_variables_names   
from innate.regression.methods import create_coef_dict

 


expression = 'a + b / (variable1_range/10000.0) + c * np.log10(variable2_range/10000)'
coef_names = extract_coef_names(expression)
print(coef_names)
coef_values = [1,2,3]
print(coef_values)
#X['a', 'b', 'c']
# Extract variables ending with '_range' (default suffix)
range_variables = extract_variables_names(expression)
print(range_variables) 
#['variable1_range', 'variable2_range']


print(create_coef_dict(coef_names, coef_values))
#{'a': 1, 'b': 2, 'c': 3}



expression = 'a + b / (variable1_range/10000.0) + c * np.log10(variable2_range/10000)'

# Fixed values for a, b, c
coefficients = {'a': 1, 'b': 4, 'c': 7}

# Specify the variable names that should vary
variable_names = ['variable1_range', 'variable2_range']  # These names should match usage in expression

# Create a function that varies with specified variables
@pytest.fixture 
def specific_function():
    expression = 'a + b / (variable1_range/10000.0) + c * np.log10(variable2_range/10000)'

    # Fixed values for a, b, c
    coefficients = {'a': 1, 'b': 4, 'c': 7}

    # Specify the variable names that should vary
    variable_names = ['variable1_range', 'variable2_range']
    return generate_specific_function(expression, coefficients, variable_names) 
#print( str(specific_function([10000, 20000, 30000],[10000, 20000, 30000])))
@pytest.mark.parametrize(
    "test, expected",
    [
        ([10000, 20000, 30000], [5.0, 5.107209969647869, 5.67318211637097])
    ]



)
def test_specific_function(test, expected):
    specific_function = generate_specific_function(expression, coefficients, variable_names) 
    np.testing.assert_almost_equal(
        specific_function([10000, 20000, 30000],[10000, 20000, 30000]), np.array(expected), decimal=7
    )


expression = 'a + b / (variable1_range/10000.0) + c * np.log10(variable2_range/10000)'

# Fixed values for a, b, c
coefficients = {'a': 1, 'b': 4, 'c': 7}

# Specify the variable names that should vary
variable_names = ['variable1', 'variable2']  # These names should match usage in expression

# Create a function that varies with specified variables
specific_function = generate_specific_function(expression, coefficients, variable_names)

# Example usage with arrays for each variable
variable1_values = np.array([10000, 20000, 30000])  # Example values for variable1
variable2_values = np.array([10000, 20000, 30000])  # Example values for variable2

 

expression = 'a + b / (variable1/10000.0) + c * np.log10(variable2/10000)'

# Extract variables
@pytest.mark.parametrize(
    "test, expected",
    [
        ('a + b / (variable1/10000.0) + c * np.log10(variable2/10000)', ['a', 'b', 'c'])
    ]

)
def test_extract_coef_names(test, expected):
    np.testing.assert_equal(
        extract_coef_names( test ),  expected) 
 



@pytest.mark.parametrize(
    "test, expected",
    [
        ((coef_names,coef_values),{'a': 1, 'b': 2, 'c': 3})
    ]

)
def test_create_coef_dict(test, expected):
    expression = 'a + b / (variable1_range/10000.0) + c * np.log10(variable2_range/10000)'
    coef_names = extract_coef_names(expression)
    coef_values = [1,2,3]
    np.testing.assert_equal(
       create_coef_dict(coef_names,coef_values),expected
    )

@pytest.mark.parametrize(
    "test, expected",
    [
        ('a + b / (variable1_range/10000.0) + c * np.log10(variable2_range/10000)',['variable1_range', 'variable2_range'])
    ]

)
def test_extract_variables_names(test, expected):
    np.testing.assert_equal(
       extract_variables_names(test ), expected
    )


# Answer should be {'a': 1, 'b': 2, 'c': 3}

# expression = 'a + b / (variable1_range/10000.0) + c * np.log10(variable2_range/10000)'

# Extract variables ending with '_range' (default suffix)
# range_variables = extract_variables_names(expression)
# print(range_variables) 
#['variable1_range', 'variable2_range']


# create_coef_dict (coef_names, coef_values)
#{'a': 1, 'b': 2, 'c': 3}