# author: Michael Hüppe
# date: 26.01.2024
# project:
import torch
import os
from modules import UNet_conditional
from ddpm_conditional import Diffusion, plot_images, sample_images, save_images
if __name__ == '__main__':
    run_name = "DDPM_conditional_pokemon"
    model_checkpoint = fr"C:\Users\mhueppe.LAPTOP-PKNG4OSF\MasterInformatik\Semester_1\ImageDiffusion\models\{run_name}\ckpt.pt"
    # Load the model
    device = "cuda"
    image_size = 32
    num_classes = 14
    model = UNet_conditional(num_classes=num_classes,
                     image_size=image_size,
                     scalingFactor=1).to(device)
    diffusion = Diffusion(noise_steps=1050, img_size=image_size, device=device)
    model.load_state_dict(torch.load(model_checkpoint))
    model.eval()  # Set the model to evaluation mode if needed
    for i in range(1000):
        labels = torch.arange(num_classes).long().to(device)
        sampled_images = sample_images(diffusion, model, num_classes, labels)
        save_images(sampled_images, os.path.join("results", run_name, f"generated_{i}.jpg"))

