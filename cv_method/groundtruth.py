import os

import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import skimage.io as io
from skimage import data_dir

root = 'G:\\PC_files\\ANU\\22S2\\COMP8715\\techlauncher\\opencv_method\\'
filename = os.listdir(root)

for file in filename:
    # images path
    print(file)
    img = Image.open('./TLCs-for-TL-22082022/'+file)
    img = ImageOps.exif_transpose(img)
    plt.imshow(img)
    plt.show()
    # get number of object manual
    n = int(input())
    plt.imshow(img)
    datas = np.asarray(plt.ginput(n, timeout=9999, show_clicks=True))
    print(datas)

    # save file
    np.save('./results/'+file.split('.')[0]+'.npy', datas)
    plt.close()


