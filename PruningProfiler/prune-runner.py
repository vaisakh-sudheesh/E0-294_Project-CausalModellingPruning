import argparse
import ModelWorkshop.Pruner as Pruner

import Models.LeNet as LeNet
import Models.ResNet as ResNet
import Models.VGG16 as VGG16
import Models.AlexNet as AlexNet
import Models.GoogleNet as GoogleNet


def parse_arguments():
    parser = argparse.ArgumentParser(description='Model Pruning Runner')
    parser.add_argument('--model_name', type=str, required=True, default="lenet")
    parser.add_argument('--pruning_method', type=str, required=True, default="l1_unstructured")
    parser.add_argument('--pruning_ratio', type=str, required=True, default="0.0")
    return parser.parse_args()

if __name__ == '__main__':
    print("Pruning runner starting...")
    args = parse_arguments()
    if args.model_name == "lenet":
        model = LeNet.LeNet()
    elif args.model_name == "resnet":
        model = ResNet.ResNet()
    elif args.model_name == "vgg16":
        model = VGG16.VGG16()
    elif args.model_name == "googlenet":
        model = GoogleNet.GoogleNet()
    elif args.model_name == "alexnet":
        model = AlexNet.AlexNet()
    else:
        raise ValueError("Invalid model name")
    if (model.load_model() == False):
        print("Error loading model, hence training")
        model.train()
        model.save_model()

    # Perform the prune operation
    pruner = Pruner.Pruner(model.get_model())
    pruner.prune(float(args.pruning_ratio), args.pruning_method)

    # Have a test run and return accuracy after pruning
    acc = model.test()

    print("Done - Accuracy after pruning: ", acc)
