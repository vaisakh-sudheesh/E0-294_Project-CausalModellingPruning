from abc import ABC, abstractmethod
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

class BaseModel(ABC):
    def __init__(self, traindataloader:DataLoader = None, testdataloader:DataLoader = None):
        self.model = None
        self.device =  (
                        "cuda" if torch.cuda.is_available()
                        else "mps" if torch.backends.mps.is_available()
                        else "cpu"
                        )
        print ('Using device ', self.device)
        self.train_dataloader = traindataloader
        self.test_dataloader = testdataloader

    def test(self) -> float:
        if (self.test_dataloader is None):
            print("Test data not provided")
            return None
        self.model.eval()
        acc = 0
        count = 0
        for X_batch, y_batch in tqdm(self.test_dataloader):
            X_batch = X_batch.to(self.device); y_batch = y_batch.to(self.device)
            y_pred = self.model(X_batch)
            acc += (torch.argmax(y_pred, 1) == y_batch).float().sum()
            count += len(y_batch)
        acc = acc / count
        acc__ = acc.cpu()
        return acc__.numpy()*100

    def train(self, n_epochs=10):
        if (self.train_dataloader is None):
            print("Train data not provided")
            return
        for epoch in range(n_epochs):
            self.model.train()
            for X_batch, y_batch in self.train_dataloader:
                X_batch = X_batch.to(self.device); y_batch = y_batch.to(self.device)
                y_pred = self.model(X_batch)
                loss = self.loss_fn(y_pred, y_batch)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
            print("Epoch %d: model accuracy %.2f%%" % (epoch, self.test()))
    
    def save_model(self, path):
        torch.save(self.model.state_dict(),path)
        print (f'Model saved to {path}')

    def load_model(self, path):
        try:
            self.model.load_state_dict(torch.load(path))
            self.model.to(self.device)
            self.model.eval()
            print( "Model loaded successfully")
            return True
        except Exception as e:
            print( f"Error: {e}")
            return False
    
    @abstractmethod
    def get_model(self):
        return self.model