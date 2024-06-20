import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
import h5py
from tensorflow.keras.saving import save_model

# Generate a 10x10 matrix with random values
np.random.seed(42)  # For reproducibility
matrix = np.random.rand(10, 10)

# Prepare input (coordinates) and output (matrix values) for training
coordinates = []
values = []

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

for i in range(10):
    for j in range(10):
        coordinates.append([i, j])
        values.append(matrix[i, j])

coordinates = np.array(coordinates)
values = np.array(values)

# Build a simple feedforward neural network
model = Sequential([
    Dense(64, input_dim=2, activation='relu'),
    Dense(64, activation='relu'),
    Dense(1)  # Output layer with one neuron for regression
])

# Compile the model
print('Model compiling')
model.compile(optimizer='adam', loss='mse')

# Train the model
print('Model fitting')
model.fit(coordinates, values, epochs=100, batch_size=4, verbose=1)

# Save the entire model to a file
model.save('my_model.h5')
tf.keras.models.save_model(model, 'my_model_models.h5')
model.save_weights('my_model.weights.h5')

# Load the weights from the file
with h5py.File('my_model.weights.h5', 'r') as f:
    weights = []
    for layer in model.layers:
        weights.append(layer.get_weights())

# Extract weights and biases for each layer
w1, b1 = weights[0]
w2, b2 = weights[1]
w3, b3 = weights[2]

# Make predictions using the NumPy implementation
numpy_predicted_values = predict_with_numpy(coordinates, w1, b1, w2, b2, w3, b3)

# Make predictions
print('Model predictions')
predicted_values = model.predict(coordinates)

# Compare the predicted values with the actual values
for i in range(len(coordinates)):
    err_percentage = (values[i]/predicted_values[i][0] - 1) * 100
    print(f"{i}) Coordinate: {coordinates[i]:}, Actual Value: {values[i]:.2f}, "
          f"Predicted Value: {predicted_values[i][0]:.2f}, Numpy Value {numpy_predicted_values[i][0]:.2f} => {err_percentage:.2f}%")

# Save the entire model to a file
model.save('my_model.h5')
tf.keras.models.save_model(model, 'my_model_models.h5')

# Evaluate the model
loss = model.evaluate(coordinates, values)
print(f"Mean Squared Error: {loss}")

