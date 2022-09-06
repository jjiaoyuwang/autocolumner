import cv2
import os

faceCascade = cv2.CascadeClassifier("haarcascade_eye.xml")  #  haarcascade_frontalface_default.xml
root = 'G:\\PC_files\\ANU\\22S2\\COMP8715\\techlauncher\\opencv_method\\gradient_output\\'
filename = os.listdir(root)

for file in filename:
    ### detectMultiScale in openCV
    # img = cv2.imread("./gradient_output/" + file)
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # # detect cascade
    # result = faceCascade.detectMultiScale(img_gray, 1.2, 5)
    # # draw box
    # for(x, y, w,h) in result:
    #     cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 5)
    #
    # # cv2.imshow("result", img)
    # # cv2.waitKey(0)
    # cv2.imwrite("./results/cascade/" + file, img)

    ### contours in openCV
    img = cv2.imread("./gradient_output/" + file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # find contour
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    draw_img = img.copy()
    # draw contour box
    ret = cv2.drawContours(draw_img, contours, -1, (0, 0, 255), 2)
    # cv2.imshow("result", ret)
    # cv2.waitKey(0)
    cv2.imwrite("./results/contour/" + file, ret)