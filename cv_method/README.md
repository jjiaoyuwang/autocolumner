# front-end integration guide

+ step 1: upload and calibrate

  - user selected an image `im` to upload (we do not want to display this image on UI. 
  But if `dash` gives us no choice but display it, we can display it without giving user any right to apply operations on it). 
  Then call `calibrate(im)` function in [calibration.py](calibration.py) to calibrate this image.
  
  - `calibrate(im)` function will return a calibrated image `im_cali`, display `im_cali` on UI. Then we give user access to `im_cali`, 
  means user can select points on it (or select small rectangle region on it, if you have implemented this function).

+ step 2.1: if user choose to use semi-auto way

  - let user annotate the spots (display the annotations, but do not modify the `im_cali`), 
  and save the coordinates of annotated points in a np.ndarray, let's call it `coords_arr`.
  Feed `(coords_arr, w)` to `rf()` function in [retention_factor.py](retention_factor.py), where `w` is the width of the `im_cali`. 
  Then `rf()` will return a list of np.ndarrays `rfs`, each array in `rfs` represents the set of retention factors calculated on one column of spots.
  
  - display `rfs` on the 'result' area on TLC tab.
  
+ step 2.2: if user choose the fully auto way means we got an empty `coords_arr`

  - feed the `im_cali` to `find_spots()` function in [detector.py](detector.py)
  
  - `find_spots()` will return a tuple `(P, rfs)`, where `rfs` is same to the `rfs` in 'step 2.1', and `P` is a coordinates matrix 
  which represent the centers of all spots we detected. (So that you can display these spots on TLC tab)
