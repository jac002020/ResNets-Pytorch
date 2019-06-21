from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
import os
from skimage import io
import numpy as np
import time
from PIL import Image

IMG_SIZE = (256,256)

class ImageNetDataset(Dataset):
    def __init__(self, data_path, is_train, train_split = 0.9, random_seed = 42, target_transform = None, num_classes = None):
        super(ImageNetDataset, self).__init__()
        self.data_path = data_path

        self.is_classes_limited = False

        if num_classes != None:
            self.is_classes_limited = True
            self.num_classes = num_classes


        self.classes = []
        class_idx = 0
        for class_name in os.listdir(data_path):
            if not os.path.isdir(os.path.join(data_path,class_name)):
                continue
            self.classes.append(
               dict(
                   class_idx = class_idx,
                   class_name = class_name,
               ))
            class_idx += 1

            if self.is_classes_limited:
                if class_idx == self.num_classes:
                    break

        if not self.is_classes_limited:
            self.num_classes = len(self.classes)

        self.image_list = []
        for cls in self.classes:
            class_path = os.path.join(data_path, cls['class_name'])
            for image_name in os.listdir(class_path):
                image_path = os.path.join(class_path, image_name)
                self.image_list.append(dict(
                    cls = cls,
                    image_path = image_path,
                    image_name = image_name,
                ))

        self.img_idxes = np.arange(0,len(self.image_list))

        np.random.seed(random_seed)
        np.random.shuffle(self.img_idxes)

        last_train_sample = int(len(self.img_idxes) * train_split)
        if is_train:
            self.img_idxes = self.img_idxes[:last_train_sample]
        else:
            self.img_idxes = self.img_idxes[last_train_sample:]

    def get_class_num(self):
        return self.num_classes

    def __len__(self):
        return len(self.img_idxes)

    def __getitem__(self, index):

        img_idx = self.img_idxes[index]
        img_info = self.image_list[img_idx]

        img = Image.open(img_info['image_path'])

        if img.mode == 'L':
            tr = transforms.Grayscale(num_output_channels=3)
            img = tr(img)

        tr = transforms.ToTensor()
        img1 = tr(img)

        width, height = img.size
        if min(width, height)>350:
            tr = transforms.Resize((350))
            img = tr(img)

        width, height = img.size
        if min(width, height)<256:
            tr = transforms.Resize((256,256))
            img = tr(img)

        tr = transforms.RandomCrop((256,256))
        img = tr(img)

        tr = transforms.ToTensor()
        img = tr(img)

        return dict(image = img, cls = img_info['cls']['class_idx'], class_name = img_info['cls']['class_name'])


# data_path = "/Users/martinsf/data/images_1/imagenet_images/"
# random_seed = int(time.time())
# dataset_train = ImageNetDataset(data_path,is_train = True, random_seed=random_seed)
#
# BATCH_SIZE = 64
# data_loader_train = DataLoader(dataset_train, BATCH_SIZE, shuffle = True)
#
# import matplotlib.pyplot as plt
#
# for x in data_loader_train:
#     print(x['image'].shape)
#     for i in range(BATCH_SIZE):
#         img = x['image'][i].numpy()
#         plt.title(x['class_name'][i])
#         plt.imshow(np.transpose(img,(1,2,0)))
#         plt.show()
#
#     break
#

