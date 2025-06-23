import os
import torch
import requests
from PIL import Image
from torchvision.models import resnet50, ResNet50_Weights

weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()
preprocess = weights.transforms()

def process_image(image_path):
    img = Image.open(image_path).convert('RGB')
    img_t = preprocess(img)
    batch_t = torch.unsqueeze(img_t, 0)
    
    with torch.no_grad():
        features = model(batch_t)
    
    return features.numpy().flatten()

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    
    temp_file = os.path.join(os.getcwd(), 'temp_image.jpg')
    with open(temp_file, 'wb') as f:
        f.write(response.content)
    
    return temp_file