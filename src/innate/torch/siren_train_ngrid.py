# Neural regression of (a single) emission line data with SIREN neural net
#
# TBD. Add test-validation-test data split.
#
# TBD. Could be possible to train a single (parametric) neural net which fits
# all lines simultanouesly. Alternatively, separate model for each.
#
#
# m.mieskolainen@imperial.ac.uk, 2024

import sys
sys.path.append("./src/")

import torch
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

import innate
import innate.torch.torch_tools as torch_tools
from innate.torch.siren import SirenNet


# -------------------------
# Open the input data

data_file = 'examples/data/emissivity_grids.nc'
emissivities = innate.DataSet.from_file(data_file)

# Loop through the lines
for i, line in enumerate(emissivities.data_labels):

    # Running example for just one line:
    if i == 0:
        
        grid_line = emissivities[line]

        ## Reshape data and parameter space coordinates for training
        temp_range, den_range = grid_line.axes_range['temp'], grid_line.axes_range['den']
        X, Y = np.meshgrid(temp_range, den_range)

        coords = np.column_stack((X.flatten(), Y.flatten()))
        values = grid_line.data.ravel()[:,None] # Add dim with [:,None]
        
        # Convert to pytorch tensor (float32)
        coords = torch.from_numpy(coords).float()
        values = torch.from_numpy(values).float()

        break # Take the first line

print(f'coords.shape = {coords.shape} | (mean,std) = ({torch.mean(coords), torch.std(coords)}')
print(f'values.shape = {values.shape} | (mean,std) = ({torch.mean(values), torch.std(values)}')

# -----------------------------
# Set reproducable seed first

torch_tools.set_seed(1234)

# Create the neural net: R^{dim_in} --> R^{dim_out}
model = SirenNet(
    dim_in     = 2,     # input dimension, e.g. 2D coordinate
    dim_out    = 1,     # output dimension per coordinate
    dim_hidden = 512,   # (hyperparam) hidden dimension
    num_layers = 4,     # (hyperparam) number of layers
    w0_initial = 30.0   # (hyperparam) init noise level for the first layer (default 30)
)

# -----------------------------------------------
# Set the computing device and transfer tensors

device = torch_tools.get_device('auto')

coords = coords.to(device)
values = values.to(device)
model  = model.to(device)


# -----------------------------------------------
# Define the optimizer

num_epoch     = 500
batch_size    = 1024

lr            = 1e-4
weight_decay  = 1e-5
max_grad_norm = 1.0

optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)


# -----------------------------------------------
# Define learning rate scheduler

scheduler_param = {
  'T_0'    : 100,      # Period
  'eta_min': lr / 10,  # Minimum learning rate
  'T_mult' : 1
}

scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, **scheduler_param)

# -----------------------------------------------
# Data loader for minibatching

dataset    = TensorDataset(coords, values)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# -----------------------------------------------

modelfile  = 'siren_model_ngrid.pth'
load_model = False

# Load the existing model
if load_model:
    torch_tools.load_torch_model(modefile  = modelfile,
                                 model     = model,
                                 optimizer = optimizer,
                                 scheduler = scheduler)

# We use MSE loss
lossfunc = torch.nn.MSELoss(reduction='mean')

for epoch in range(1,num_epoch+1):
    
    total_loss = 0
    num_batch  = 0
    
    # Minibatch training loop
    for batch_idx, (inputs, targets) in enumerate(dataloader):
        
        optimizer.zero_grad() #!
        
        # Compute the model prediction and MSE loss
        preds = model(inputs)
        loss  = lossfunc(preds, targets)
        loss.backward()
        
        # Clip gradients by norm
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)

        optimizer.step()
        
        # Save for output
        total_loss += loss.item()
        num_batch += 1

    scheduler.step() # Step per epoch
    
    total_loss = total_loss / num_batch

    print(f'epoch = {epoch} / {num_epoch} | loss = {total_loss:0.3E} | lr = {scheduler.get_last_lr()[0]:0.3E}')
    
    with torch.no_grad():
        if (epoch % 10) == 0:
            
            # Save the model
            torch_tools.save_torch_model(modelfile = modelfile,
                                         model     = model,
                                         optimizer = optimizer,
                                         scheduler = scheduler)

