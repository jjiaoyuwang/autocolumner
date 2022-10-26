"""
This module is for calculating RFs, given coordinates of spots detected
"""

import numpy as np
from sklearn.cluster import DBSCAN
from scipy.optimize import curve_fit
import os
import utils
import warnings

warnings.filterwarnings('ignore')

beta = 2
std_th = 0.06
perp_th = 0.04


def total_ls(M: np.ndarray):
    """total least-square line fitting, we use the normal ls instead"""
    m, _ = M.shape
    A = M - np.mean(M, axis=0)

    w, v = np.linalg.eig(A.T @ A)
    p = v[np.argmin(w)]

    a, b = p
    c = -p @ np.mean(M, axis=0)
    theta = np.array([a, b, c])

    _M = np.hstack((M, np.ones((m, 1))))
    D = np.abs(_M @ theta)

    return (a, b, c), D


def cluster(M: np.ndarray):
    """for all spots on image, cluster them into columns"""
    l = []
    m, n = M.shape
    x, y = M.T
    sigma = np.std(x)  # std of spots in x-dimension (horizontal)

    if sigma <= std_th * w:  # if spots are very close, do not need to cluster them
        l.extend([M])
    else:
        eps = sigma / beta  # threshold of neighbor dist for DBSCAN
        db = DBSCAN(eps=eps, min_samples=1).fit(x.reshape((m, 1)))
        labels_ = db.labels_
        K = set(labels_)  # set of clusters (i.e. {0,1,2,3..}), 0 -> outliers
        if K != {0}:
            for k in K:
                M_k = M[np.argwhere(labels_ == k).squeeze(axis=1)]
                l.extend(cluster(M_k))
        else:
            l.extend([M])

    return l


def ls(M: np.ndarray):
    """least-square line fitting"""
    def func(y, a, b, c):
        return (-b * y - c) / a
    x, y = M.T
    popt = curve_fit(func, y, x)[0]  # fitted line, please refer to scipy.optimize.curve_fit
    return popt


def perp(C: np.ndarray, popt: np.ndarray):
    """calculate perpendicular distances between fitted line and spots in a column (same cluster)"""
    m, n = C.shape
    C_1 = np.hstack((C, np.ones((m, 1))))  # padding (x,y) with 1, just convenient for calculation
    d = np.abs(C_1 @ np.array(popt)) / np.linalg.norm(np.array(popt[:-1]))  # perpendicular distances
    return d


def opt(clusterList: list):
    """apply fine-tuning after clustering all spots"""
    indices = []
    cl = []
    if len(clusterList) == 1:  # singular case, only one column/cluster
        return clusterList
    for i in range(len(clusterList)):
        if i in indices:
            continue  # if we already fine-tuned this column, skip it
        C = clusterList[i]
        if i == len(clusterList) - 1:
            cl.append(C)  # no column on the right to compare, then stop
        else:
            C_r = np.vstack((C, clusterList[i + 1]))  # attach the right column to current column
            if len(C_r) < 3:  # singular case, one spot in each column, can not fit lines
                cl.append(C)  # so consider as 2 distinct columns
            else:
                d = perp(C_r, ls(C_r))  # fit all spots in 2 columns with a vertical line, and calculate distances
                if np.mean(d) < perp_th * w:  # these 2 columns are close and can be represented as one fitted line
                    indices.extend([i, i + 1])  # integrate them into one column
                    cl.append(C_r)
                else:
                    cl.append(C)

    # we also need to include the start point and end point for each column
    for i, C in enumerate(cl):
        x, _ = np.mean(C, axis=0)
        y = L @ np.array([x, 1])
        P = np.stack((np.array([x, x]), y))
        cl[i] = np.vstack((C, P.T))

    return cl


def rf_calc(C: np.ndarray):
    """calculate RFs"""
    _, y = C.T
    y = np.abs(y - np.max(y))
    y.sort()
    y = y / np.max(y)

    return np.round(y[(0 < y) & (y < 1)], decimals=3)


def rf(M: np.ndarray, width, line_coefficient):
    """pipeline of RFs calculation"""
    global w
    global L
    w = width
    L = line_coefficient

    rfs = []
    cl = cluster(M)  # cluster all spots into columns
    cl.sort(key=lambda x: np.mean(x, axis=0)[0])  # order columns from left to right
    cl = opt(cl)  # integrate close neighbor columns
    for c in cl:
        rfs.append(rf_calc(c))

    return rfs


if __name__ == '__main__':
    imDir = 'dataset_perspective_transformed/'
    arrDir = 'ground_truth_coordinates/'
    files = os.listdir(imDir)

    for f in files:
        im, gray = utils.imread(imDir + f)
        h, w = gray.shape
        _, line_coefficient = utils.mask(gray)
        M = np.load(arrDir + f.split('.')[0] + '.npy')
        rfs = rf(M, w,line_coefficient)
        print(rfs)
