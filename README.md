# E0-294_Project-CausalModellingPruning


## Downloading ImageNet Dataset

To download the ImageNet dataset, follow the steps below:

1. Run the following command to download the ImageNet validation dataset in a tar file:
    ```
    wget https://image-net.org/data/ILSVRC/2012/ILSVRC2012_img_val.tar --no-check-certificate
    ```

2. After downloading the tar file, unzip it into the desired folder using the following command:
    ```
    tar -xvf ILSVRC2012_img_val.tar -C /raid/home/anishkar/PruningTest/imagenet/val
    ```

## Additional Helper Files

Additionally, there are two little helper files required for processing the ImageNet dataset. You can download them into the ImageNet root folder (the one that contains the ILSVRC folder) by following the steps below:

1. Navigate to the ImageNet root folder.

2. Run the following commands to download the helper files:
    ```
    cd imagenet
    wget https://raw.githubusercontent.com/raghakot/keras-vis/master/resources/imagenet_class_index.json
    wget https://gist.githubusercontent.com/paulgavrikov/3af1efe6f3dff63f47d48b91bb1bca6b/raw/00bad6903b5e4f84c7796b982b72e2e617e5fde1/ILSVRC2012_val_labels.json
    ```

With these steps, you will have downloaded the ImageNet dataset and the necessary helper files for further processing and analysis.
