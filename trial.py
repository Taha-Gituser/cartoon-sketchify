import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import cv2
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt


model = torch.hub.load('pytorch/vision:v0.9.0', 'deeplabv3_resnet101', pretrained=True)
model.eval()


data_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])

def detect_edges(image_path):
  
    image = Image.open(image_path).convert("RGB")
    input_tensor = data_transform(image).unsqueeze(0)  # Add batch dimension

    # Perform inference
    with torch.no_grad():
        output = model(input_tensor)['out'][0]  # Get the output and remove the batch dimension

    # Convert the output tensor to a PIL image
    output = output.argmax(0).byte()
    edge_map = transforms.ToPILImage()(output)

    return image, edge_map

def cartoonize_image(image_path):
    img = cv2.imread(image_path)
 
    scale_percent = 50  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Increase blockSize and C parameters for more aggressive thresholding
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=35, C=20)

    # Increase color intensity in bilateral filter
    color = cv2.bilateralFilter(img, 9, 200, 200)
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return img, edges, cartoon



def process_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg; *.jpeg; *.png")])
    if file_path:
        # Get the original image and edges image from cartoonize_image function
        original, edges, cartoon = cartoonize_image(file_path)

        # Create a figure and axis objects
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        # Display the original image
        axs[0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        axs[0].set_title('Original Image')
        axs[0].axis('off')

        # Display the edges image
        axs[1].imshow(edges, cmap='gray')
        axs[1].set_title('Edges Image')
        axs[1].axis('off')

        # Display the cartoonized image
        axs[2].imshow(cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB))
        axs[2].set_title('Cartoonized Image')
        axs[2].axis('off')

        plt.show()



root = tk.Tk()
root.title("Select and Process Image")


select_button = tk.Button(root, text="Select and Process Image", command=process_image)
select_button.pack(padx=10, pady=10)

root.mainloop()
