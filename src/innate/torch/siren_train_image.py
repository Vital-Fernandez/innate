# Neural regression of brain image data with SIREN neural net
#
# Number of iterations required may be O(10000)
#
# m.mieskolainen@imperial.ac.uk, 2024

import sys
sys.path.append("./src/")

import torch
import torchvision.transforms as transforms
import numpy as np
from PIL import Image

import innate.torch.torch_tools as torch_tools
from innate.torch.siren import SirenNet, SirenImageWrapper


# -------------------------
# Open the input image file

img_jpeg = Image.open('examples/data/brains.jpeg')

# Define and apply the transformation to convert the image to a tensor
transform = transforms.ToTensor()
img = transform(img_jpeg).float()

# Add [dummy] batch dimension to beginning
img = img.unsqueeze(0)

torch_tools.visualize_img(img=img, savename=f'input_image.jpeg')
# -----------------------------


# -----------------------------
# Set reproducable seed first

torch_tools.set_seed(1234)

    # Create the neural net: R^{dim_in} --> R^{dim_out}
net = SirenNet(
    dim_in     = 2,     # input dimension, e.g. 2D coordinate
    dim_out    = 1,     # output dimension per coordinate, e.g. for RGB image (3)
    dim_hidden = 512,   # (hyperparam) hidden dimension
    num_layers = 4,     # (hyperparam) number of layers
    w0_initial = 30.0   # (hyperparam) init noise level for the first layer (default 30)
)

# Helper wrapper for image signals
model = SirenImageWrapper(
    net,
    image_height = img.shape[-2],
    image_width  = img.shape[-1],
)

print(f'img.shape = {img.shape} | (mean,std) = ({torch.mean(img.flatten()):0.2f}, {torch.std(img.flatten()):0.2f})')

# -----------------------------------------------
# Set the device and transfer tensors

device = torch_tools.get_device('auto')

img    = img.to(device)
model  = model.to(device)


# -----------------------------------------------
# Define the optimizer

num_iter      = 10000
lr            = 3e-4
weight_decay  = 1e-5
max_grad_norm = 1.0

optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)


# -----------------------------------------------
# Define learning rate scheduler

scheduler_param = {
  'T_0'    : 500,       # Period
  'eta_min': lr / 10,   # Minimum learning rate
  'T_mult' : 1
}

scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, **scheduler_param)
# -----------------------------------------------

modelfile  = 'siren_model.pth'
load_model = False
visualize  = False

# Load the existing model
if load_model:
    torch_tools.load_torch_model(modelfile = modelfile,
                                 model     = model,
                                 optimizer = optimizer,
                                 scheduler = scheduler)

# Training loop
# (single batch gradient descent == full image at once)
for i in range(1,num_iter+1):

    optimizer.zero_grad() #!
    loss = model(img) # MSE loss inside the wrapper
    loss.backward()
    
    # Clip gradients by norm
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
        
    optimizer.step()
    scheduler.step()
    
    print(f'iter = {i} / {num_iter} | loss = {loss.item():0.3E} | lr = {scheduler.get_last_lr()[0]:0.3E}')
    
    with torch.no_grad():
        if (i % 10) == 0:
            
            # This will evaluate the model prediction implicitly
            # at the training image point grid coordinates
            pred_img = model()
            
            # Visualize
            if visualize:
                torch_tools.visualize_img(img=pred_img, savename=f'pred_image_iter_{i}.jpeg')
            
            # Save the model
            torch_tools.save_torch_model(modelfile = modelfile,
                                         model     = model,
                                         optimizer = optimizer,
                                         scheduler = scheduler)
