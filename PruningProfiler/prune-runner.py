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
    parser.add_argument('--pruning_ratio', type=float, required=True, default="0.0")
    parser.add_argument('--batchsz', type=int, required=False, default="64")
    parser.add_argument('--runnercnt', type=int, required=False, default="8")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    print("Pruning runner starting...  with ",
                args.model_name,
                " model and ", args.pruning_method,
                " method and ", args.pruning_ratio, " ratio",
                " batch size ", args.batchsz, " runner count ", args.runnercnt)
    if args.model_name == "lenet":
        model = LeNet.LeNet()
    elif args.model_name == "resnet":
        model = ResNet.ResNet(args.batchsz, args.runnercnt)
    elif args.model_name == "vgg16":
        model = VGG16.VGG16(args.batchsz, args.runnercnt)
    elif args.model_name == "googlenet":
        model = GoogleNet.GoogleNet(args.batchsz, args.runnercnt)
    elif args.model_name == "alexnet":
        model = AlexNet.AlexNet(args.batchsz, args.runnercnt)
    else:
        raise ValueError("Invalid model name")
    if (model.load_model() == False):
        print("Error loading model, hence training")
        model.train()
        model.save_model()

    # Perform the prune operation
    pruner = Pruner.Pruner(model.get_model())
    pruner.prune(args.pruning_ratio, args.pruning_method)

    # Have a test run and return accuracy after pruning
    acc = model.test()

    print("Done - Accuracy after pruning: ", acc)
