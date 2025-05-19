import os
import requests
from PIL import Image
import numpy as np
import torch
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights
import io

# Initialize ResNet50 model
weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()
preprocess = weights.transforms()

def process_image(image_path):
    """Process image and extract features"""
    img = Image.open(image_path).convert('RGB')
    img_t = preprocess(img)
    batch_t = torch.unsqueeze(img_t, 0)
    
    with torch.no_grad():
        features = model(batch_t)
    
    return features.numpy().flatten()

def download_image(url):
    """Download image from URL to temporary file"""
    response = requests.get(url)
    response.raise_for_status()
    
    # Create a temporary file
    temp_file = os.path.join(os.getcwd(), 'temp_image.jpg')
    with open(temp_file, 'wb') as f:
        f.write(response.content)
    
    return temp_file