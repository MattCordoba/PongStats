__author__ = 'Matt Cordoba'
# import the necessary packages
import numpy as np
import cv2
import time
def functionDetectBall(image_path):
    # load the image
    image = cv2.imread(image_path)
    # define the list of boundaries

    orange_boundaries = [ ([25, 146, 190], [62, 174, 250])]
    lower,upper = orange_boundaries[0]
    # create NumPy arrays from the boundaries
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    # find the colors within the specified boundaries and apply
    # the mask
    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask=mask)
    l = len(output)*len(output[0])
    val = np.count_nonzero(output)
    percentThreshold = val *100.0 / l
    if(percentThreshold > 2): #greater than 2%
        print('ball detected')
        return True
    print('no ball detected')
    return False
t = time.time()
functionDetectBall( 'rsz_ball_orange.jpg')
print(time.time() - t)
t = time.time()
functionDetectBall( 'ball_orange.jpg')
print(time.time() - t)
t = time.time()
functionDetectBall('black.JPG')
print(time.time() - t)
