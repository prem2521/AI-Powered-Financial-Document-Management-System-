import torch
import torch.nn as nn
from torchvision import transforms
import timm
import cv2
import numpy as np
from PIL import Image

class DeepfakeDetector(nn.Module):
    def __init__(self, model_name='tf_efficientnet_b0_ns', num_classes=1, pretrained=True):
        super(DeepfakeDetector, self).__init__()
        # Use a pre-trained EfficientNet from timm
        self.encoder = timm.create_model(model_name, pretrained=pretrained)

        # Modify the classifier head for binary classification (Real vs Fake)
        num_features = self.encoder.classifier.in_features
        self.encoder.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, num_classes)
        )

        # Save the target layer for Grad-CAM
        self.target_layer = self.encoder.blocks[-1]
        self.gradients = None
        self.activations = None

        # Hook into the target layer
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def forward(self, x):
        return self.encoder(x)

    def get_activations_gradient(self):
        return self.gradients

    def get_activations(self, x):
        return self.activations

class DeepfakeInference:
    def __init__(self, model_path=None, device='cpu'):
        self.device = torch.device(device)
        self.model = DeepfakeDetector().to(self.device)

        if model_path:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                print(f"Loaded model weights from {model_path}")
            except Exception as e:
                print(f"Warning: Could not load model weights: {e}. Using uninitialized/pretrained weights.")

        self.model.eval()

        # Standard ImageNet normalization for EfficientNet
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict(self, face_pil):
        """
        Predict if a single face image is real or fake.
        Returns probability of being FAKE (1.0 = fake, 0.0 = real).
        """
        tensor = self.transform(face_pil).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(tensor)
            # Using sigmoid since it's a single output node
            prob = torch.sigmoid(output).item()

        return prob

    def generate_gradcam(self, face_pil):
        """
        Generate a Grad-CAM heatmap for a face image.
        Requires gradients, so we temporarily enable them.
        """
        self.model.train() # Need train mode or requires_grad for backward
        tensor = self.transform(face_pil).unsqueeze(0).to(self.device)
        tensor.requires_grad = True

        output = self.model(tensor)

        self.model.zero_grad()
        output.backward(torch.ones_like(output))

        gradients = self.model.get_activations_gradient()
        activations = self.model.get_activations(tensor)

        # Global average pooling on gradients
        pooled_gradients = torch.mean(gradients, dim=[0, 2, 3])

        # Weight the channels by corresponding gradients
        for i in range(activations.size(1)):
            activations[:, i, :, :] *= pooled_gradients[i]

        # Average the channels of the activations
        heatmap = torch.mean(activations, dim=1).squeeze()
        heatmap = torch.relu(heatmap)
        heatmap /= torch.max(heatmap) if torch.max(heatmap) > 0 else 1.0

        heatmap_np = heatmap.cpu().detach().numpy()

        # Resize heatmap to match image size (224x224)
        heatmap_np = cv2.resize(heatmap_np, (face_pil.size[0], face_pil.size[1]))
        heatmap_np = np.uint8(255 * heatmap_np)

        # Apply colormap
        heatmap_color = cv2.applyColorMap(heatmap_np, cv2.COLORMAP_JET)

        # Superimpose
        face_np = np.array(face_pil)
        # Convert RGB to BGR for OpenCV
        face_bgr = cv2.cvtColor(face_np, cv2.COLOR_RGB2BGR)

        superimposed_img = heatmap_color * 0.4 + face_bgr
        superimposed_img = np.uint8(np.clip(superimposed_img, 0, 255))

        self.model.eval()
        return superimposed_img
