import numpy as np
import innate
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
import h5py


def relu(x):
    return np.maximum(0, x)


# Implement the forward pass using NumPy
def predict_with_numpy(coordinates, w1, b1, w2, b2, w3, b3):
    # Perform the forward pass manually
    # Input to first hidden layer
    h1 = relu(np.dot(coordinates, w1) + b1)

    # First hidden layer to second hidden layer
    h2 = relu(np.dot(h1, w2) + b2)

    # Second hidden layer to output layer
    output = np.dot(h2, w3) + b3

    return output


# Load the data
data_file = '../data/emissivity_grids.nc'
emissivities = innate.DataSet.from_file(data_file)

# Define nn design
model = Sequential([
    Dense(64, input_dim=2, activation='relu'),
    Dense(64, activation='relu'),
    Dense(1)])

model.compile(optimizer='adam', loss='mse')

# Loop through the lines
for i, line in enumerate(emissivities.data_labels):

    # Running example for just one line:
    if i == 0:

        grid_line = emissivities[line]

        # Reshape data and parameter space coordinates for training
        temp_range, den_range = grid_line.axes_range['temp'], grid_line.axes_range['den']
        X, Y = np.meshgrid(temp_range, den_range)

        coordinates = np.column_stack((X.flatten(), Y.flatten()))
        values = grid_line.data.ravel()

        # Fit the model a simple feedforward neural network
        model.fit(coordinates, values, epochs=100, batch_size=2000, verbose=1)

        # Save the trained model and coefficients
        output_model_file = f'../data/{line}_nn_model_v1.h5'
        model.save(output_model_file)
        output_weights_file = f'../data/{line}_nn_model_v1.weights.h5'
        model.save_weights(output_weights_file)

        # Recover coefficients
        with h5py.File('my_model.weights.h5', 'r') as f:
            weights = []
            for layer in model.layers:
                weights.append(layer.get_weights())
        w1, b1 = weights[0]
        w2, b2 = weights[1]
        w3, b3 = weights[2]

        # Compare prediction from model with manual numpy function
        test_coord, test_value = np.atleast_2d(coordinates[1000]), values[1000]

        keras_prediction = model.predict(test_coord)
        np_prediction = predict_with_numpy(test_coord, w1, b1, w2, b2, w3, b3)

        print('Keras prediction', keras_prediction)
        print('Manual prediction', np_prediction)
        print('True value', test_value)


