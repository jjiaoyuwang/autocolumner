import os

import cv2 as cv
import numpy as np
import numpy.linalg as la
from matplotlib import pyplot as plt
from scipy import optimize

import findLine as fl


def read(filename):
    """read gray scale image"""
    im = cv.imread(filename)
    gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    return im, gray


def denoise(src, blur=3):
    """denoise process: median blur + histogram equalise + opening"""
    blur = cv.medianBlur(src, blur)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(blur)
    kernel = np.ones((7, 7), np.uint8)
    opening = cv.morphologyEx(cl, op=cv.MORPH_OPEN, kernel=kernel)
    return opening


def binarize(src, blur=3):
    """Gaussian thresholding: cvt to binary and eliminate noise points on binary im"""
    th = cv.adaptiveThreshold(src, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    dst = cv.medianBlur(th, blur)
    dst_invert = cv.bitwise_not(dst)
    # plt.imshow(dst_invert, cmap='gray'), plt.title('Threshold'), plt.show()
    return dst_invert


def fit_circle(cnt):
    """find the circle that best fit the points on contour"""
    def off_bound(circle):
        """boundary test"""
        cx, cy, r = circle
        if r < e_radius * min(w, h):
            return True
        if cx - r >= w or cx + r <= 0:
            return True
        if over_line((cx, cy, r)):
            return True
        return False

    def dist(c):
        """array of distances from the points on contour to the centre of the fitted circle"""
        cx, cy = c
        return np.sqrt(np.power(x - cx, 2) + np.power(y - cy, 2))

    def f(c):
        """objective function"""
        d = dist(c)
        r = np.mean(d)
        return d - r

    P = cnt.squeeze()  # opencv is weired on this data structure, always squeeze a contour before apply operations
    x, y = P.T
    c = np.mean(P, axis=0)  # initial center by taking average

    output = optimize.leastsq(f, c)  # least-square to approximate null space
    cx, cy = output[0]  # get centre of the fitted circle
    r = np.mean(dist((cx, cy)))  # calc radius
    circle = cx, cy, r
    if off_bound(circle):
        return None

    return circle


def opt(contours):
    """remove some small arcs"""
    ratio = []
    circles = []
    counter = 0
    for i, cnt in enumerate(contours):
        circle = fit_circle(cnt)
        circles.append(circle)
        M = cv.moments(cnt)
        if circle is None:
            counter += 1
        if circle is not None and M['m00'] != 0:
            cx, cy, r = circle
            center = np.array([cx, cy])
            c_x = int(M['m10'] / M['m00'])
            c_y = int(M['m01'] / M['m00'])
            centroid = np.array([c_x, c_y])
            L2 = la.norm(centroid - center)  # dist from centre of the fitted circle to the centroid of contour
            ratio.append(L2 / r)  # calc ratio L2/R, the smaller the arc the larger the ratio
        else:
            ratio.append(-1)

    ratio = np.array(ratio)
    bar = np.quantile(ratio[ratio != -1], e_bar)
    indices = np.argwhere((-1 != ratio) & (ratio <= bar)).squeeze().astype(int)
    # indices = ratio[np.argwhere(ratio is not None and ratio<=bar).squeeze()][:,1].astype(int)

    return indices, [circles[i] for i in indices]


def contour(f):
    """main func"""
    for filename in f:
        global gray, h, w
        im, gray = read(dirPath + filename)
        h, w = gray.shape

        binary = binarize(denoise(gray, blur=5))
        mask = np.zeros(binary.shape, np.uint8)

        contours, hierarchy = cv.findContours(image=binary, mode=cv.RETR_CCOMP, method=cv.CHAIN_APPROX_SIMPLE)

        # draw all contours
        dst = im.copy()
        cv.drawContours(dst, contours, -1, (0, 255, 0), 3)
        # plt.imshow(cv.cvtColor(dst, cv.COLOR_BGR2RGB)), plt.title('all contours'), plt.show()

        # remove contours off boundary
        dst = im.copy()
        v = valid(contours)
        if len(v) != 0:
            contours = v
        cv.drawContours(dst, contours, -1, (0, 255, 0), 3)
        # plt.imshow(cv.cvtColor(dst, cv.COLOR_BGR2RGB)), plt.title('in line contours'), plt.show()

        # remove small and flat contours
        dst = im.copy()
        th = thresholding(contours)
        if th is None:
            print(f'{filename} failed: no potential spots found between upper line and bottom line')
            continue
        contours, rect = thresholding(contours)
        cv.drawContours(dst, contours, -1, (0, 255, 0), 3)
        for r in rect:
            box = cv.boxPoints(r)
            box = np.int0(box)
            cv.drawContours(dst, [box], 0, (0, 0, 255), 2)
        # plt.imshow(cv.cvtColor(dst, cv.COLOR_BGR2RGB)), plt.title('large contours'), plt.show()

        # remove all small arcs
        dst = im.copy()
        indices, circles = opt(contours)
        rect = [rect[i] for i in indices]

        for r in rect:
            box = cv.boxPoints(r)
            box = np.int0(box)
            cv.drawContours(dst, [box], 0, (0, 0, 255), 2)
        # for c in circles:
        #     cx,cy,r = c
        #     cv.circle(dst,center=(int(cx),int(cy)),radius=int(r),color=[0,255,0])
        plt.imshow(cv.cvtColor(dst, cv.COLOR_BGR2RGB)), plt.title(f'{filename}'), plt.show()
        cv.imwrite('spots/' + filename, dst)


def thresholding(contours):
    """for rounding rects, we prefer large and square"""
    cntArea = [cv.contourArea(cnt) for cnt in contours]
    th = e_area ** 2 * (w * h)
    largeContours = [contours[i] for i in range(len(cntArea)) if cntArea[i] > th]  # get large enough contours
    if len(largeContours) < 2:
        return None
    rect = [cv.minAreaRect(cnt) for cnt in largeContours]
    S = np.array([r[1] for r in rect])
    ratio = np.max(S, axis=1) / np.min(S, axis=1)  # measure how likely the rect to be a square
    rectArea = -S[:, 0] * S[:, 1]  # measure how large the rect is
    scaledRatio = (ratio - np.min(ratio)) / (np.max(ratio) - np.min(ratio))  # normalize ratio
    scaledArea = (rectArea - np.min(rectArea)) / (np.max(rectArea) - np.min(rectArea))  # normalize area

    loss = scaledArea + e_ratio * scaledRatio  # compare to large, square is less important
    bar = np.quantile(loss, q=e_bar)
    indices = np.argwhere(loss < bar).squeeze().astype(int)

    return [largeContours[i] for i in indices], [rect[i] for i in indices]


def over_line(c, cnt=None):
    """remove contours which are too close to the boundaries or even exceed the boundaries"""
    if cnt is not None:
        cnt = cnt.squeeze()
    r = 0
    near = False
    if len(c) == 2:
        x, y = c
        near = True
    else:
        x, y, r = c
    u, l = fl.hough_line(gray)
    um, uc, _ = fl.l_eq(u)
    lm, lc, _ = fl.l_eq(l)

    y_u = um * x + uc - r
    y_l = lm * x + lc + r
    if y_l >= y >= y_u:
        if near:
            d = (np.max(cnt, axis=0) - np.min(cnt, axis=0)).reshape(2)
            dy = e_bound * h
            dx = e_bound * w * 2
            if (y_l - dy <= y or y <= y_u + dy) and d[1] < dy:
                return True
            if (x <= dx or x > w - dx) and d[0] < dx:
                return True
        return False
    return True


def valid(contours):
    c = []
    for cnt in contours:
        M = cv.moments(cnt)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            if not over_line((cx, cy), cnt=cnt):
                c.append(cnt)
    return c


if __name__ == '__main__':
    # hyper parameters
    e_radius = 1e-2  # minimum(r/min(w,h)) r is the radius of the circle
    e_area = 1e-2  # minimum area of a contour = (e_area*w) * (e_area*h)
    e_ratio = 0.5  # the balance factor between scaledArea nad scaledRatio (scaledRatio is less dominant)
    e_bar = 0.9  # we view the last 10% are noise and eliminate them
    e_bound = 2e-2  # All points within e_bound*h from the upper and lower bounds are noise
                    # all points within 2*e_bound*w from the left and right bounds are noise

    dirPath = 'dataset_perspective_transformed/'
    f = os.listdir(dirPath)
    contour(f)
