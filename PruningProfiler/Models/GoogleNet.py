from Models.BaseModel import BaseModel
import Data.ImageNet as ImageNet

import torchvision

class GoogleNet(BaseModel):
    def __init__(self):
        self.__MODEL_FILENAME = "Models/googlenet.pth"
        self.kaggledataset = ImageNet.ImageNetKaagle()
        super().__init__(testdataloader=self.kaggledataset.dataloader)

        self.model = torchvision.models.googlenet(weights = "DEFAULT")
        self.model.to(self.device)
        self.model.eval()

    def load_model(self):
        pass

    def save_model(self):
        pass

    def get_model(self):
        return self.model

