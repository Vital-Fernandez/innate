# Torch aux tools
#
# m.mieskolainen@imperial.ac.uk, 2024

import numpy as np
import torch
import random
import matplotlib.pyplot as plt


def get_device(device: str='auto'):
        
    # Force specific
    if device != 'auto':
        return torch.device(device)
    
    # Check if CUDA is available
    if torch.cuda.is_available() and device == 'auto':
        device = torch.device("cuda")
        print("get_device: CUDA device selected:", torch.cuda.get_device_name(0))
    else:
        device = torch.device("cpu")
        print("get_device: No CUDA device available, using CPU.")

    return device

def set_seed(seed: int):
    """
    Set random seed
    """
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if you are using multi-GPU.
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def visualize_img(img: torch.Tensor, remove_batch_dim: bool=True,
                  savename: str=None, dpi: float=120):
    """
    Visualize torch tensor image
    """
    
    if remove_batch_dim:
        # Remove the batch dimension for visualization (from (1, C, H, W) to (C, H, W))
        img_tensor = img.squeeze(0)
    
    # Convert the tensor to a NumPy array and transpose it to (H, W, C)
    img_np = img_tensor.permute(1, 2, 0).detach().cpu().numpy()

    # Visualize the image using Matplotlib
    plt.imshow(img_np)
    plt.axis('off')  # Turn off axis numbers and ticks
    
    if savename is None:
        plt.show()
    else:
        plt.savefig(savename, bbox_inches='tight', dpi=dpi)
        print(f"visualize_img: Saved image to '{savename}'")


def load_torch_model(modelfile: str, model, optimizer=None, scheduler=None):
    """
    Load torch model (+ optimizer, + scheduler) from a file
    """
    checkpoint = torch.load(modelfile)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    if scheduler is not None:
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    
    print(f"load_torch_model: Model loaded from '{modelfile}'")


def save_torch_model(modelfile: str, model, optimizer=None, scheduler=None):
    """
    Save torch model (+ optimizer, + scheduler)
    """

    torch.save({
        'model_state_dict':     model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict() if optimizer is not None else None,
        'scheduler_state_dict': scheduler.state_dict() if scheduler is not None else None,
    }, modelfile)

    print(f"save_torch_model: Torch model saved to '{modelfile}'")

