import cv2
import os
import numpy as np
from matplotlib import pyplot as plt

root = 'G:\\PC_files\\ANU\\22S2\\COMP8715\\techlauncher\\opencv_method\\'

def scharr(img):
    scharrx = cv2.Scharr(img, cv2.CV_64F, 1, 0)
    scharrx = cv2.convertScaleAbs(scharrx)
    scharry = cv2.Scharr(img, cv2.CV_64F, 0, 1)
    scharry = cv2.convertScaleAbs(scharry)
    scharr = cv2.addWeighted(scharrx, 0.5, scharry, 0.5, 0)
    return scharr

def print_hist(img):
    h, w = img.shape[:2]
    flaten = img.reshape([h * w, ])
    hist, bin, patch = plt.hist(flaten, 256)
    plt.xlabel("gray")
    plt.ylabel("pixels")
    plt.axis([0, 255, 0, np.max(hist)])
    plt.show()


filename = os.listdir(root)
for file in filename:
    img = cv2.imread("./dataset/" + file, 0)
    # print_hist(img)
    # cv2.imshow('result', scharr(img))
    # cv2.waitKey(0)
    cv2.imwrite("./gradient_output/"+file, scharr(img))