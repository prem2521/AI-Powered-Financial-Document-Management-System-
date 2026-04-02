import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging
import sys

# Add the backend app core path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))
from app.core.model import DeepfakeDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepfakeDataset(Dataset):
    """
    A simple dataset that expects a directory structure:
    data_dir/
      real/
        image1.jpg
        ...
      fake/
        image1.jpg
        ...
    """
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []

        real_dir = os.path.join(data_dir, 'real')
        fake_dir = os.path.join(data_dir, 'fake')

        if os.path.exists(real_dir):
            for img_name in os.listdir(real_dir):
                self.image_paths.append(os.path.join(real_dir, img_name))
                self.labels.append(0.0) # 0 for real

        if os.path.exists(fake_dir):
            for img_name in os.listdir(fake_dir):
                self.image_paths.append(os.path.join(fake_dir, img_name))
                self.labels.append(1.0) # 1 for fake

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = torch.tensor([self.labels[idx]], dtype=torch.float32)

        if self.transform:
            image = self.transform(image)

        return image, label

def train_model(data_dir, epochs=10, batch_size=32, lr=1e-4, save_path='model.pth'):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    dataset = DeepfakeDataset(data_dir, transform=transform)
    if len(dataset) == 0:
        logger.error(f"No images found in {data_dir}. Expected 'real' and 'fake' subdirectories.")
        return

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    model = DeepfakeDetector(pretrained=True).to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_acc = 0.0

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)

        epoch_loss = running_loss / len(train_loader.dataset)

        # Validation
        model.eval()
        all_preds = []
        all_labels = []
        val_loss = 0.0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)

                preds = torch.sigmoid(outputs).round()
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())

        val_loss /= len(val_loader.dataset)
        acc = accuracy_score(all_labels, all_preds)
        prec = precision_score(all_labels, all_preds, zero_division=0)
        rec = recall_score(all_labels, all_preds, zero_division=0)
        f1 = f1_score(all_labels, all_preds, zero_division=0)

        logger.info(f"Epoch {epoch+1}/{epochs} - Train Loss: {epoch_loss:.4f} - Val Loss: {val_loss:.4f} - Acc: {acc:.4f} - Prec: {prec:.4f} - Rec: {rec:.4f} - F1: {f1:.4f}")

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), save_path)
            logger.info(f"Saved best model with accuracy {best_acc:.4f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Deepfake Detector")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to training data directory")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--save_path", type=str, default="model_best.pth", help="Path to save the model")

    args = parser.parse_args()
    train_model(args.data_dir, args.epochs, args.batch_size, args.lr, args.save_path)
