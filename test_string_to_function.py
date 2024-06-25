


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

# Compute the result using the custom specific function
result = specific_function(variable1_values, variable2_values)
print(result)
 #[5.0 5.107209969647869 5.67318211637097]

expression = 'a + b / (variable1/10000.0) + c * np.log10(variable2/10000)'

# Extract variables
coef_names = extract_coef_names(expression)
print(coef_names)
coef_values = [1,2,3]
print(coef_values)
#X['a', 'b', 'c']
create_coef_dict(coef_names,coef_values )
# Answer should be {'a': 1, 'b': 2, 'c': 3}


# Extract variables ending with '_range' (default suffix)
range_variables = extract_variables_names(expression)
print(range_variables) 
#['variable1_range', 'variable2_range']