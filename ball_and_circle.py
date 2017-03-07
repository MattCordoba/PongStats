__author__ = 'Matt Cordoba'
import cv2
import numpy as np
import sys
from collections import deque
#cap = cv2.VideoCapture(0) #webcam
cap = cv2.VideoCapture('orange_shots.mp4')
lower = (18, 120, 180)# 22 180 180
upper = (26, 255, 255) #18 140 236
video_path = 'orange_shots.mp4'#'orange_ball.mp4'#None#'ball_quick_toss.mp4'#None#'orange_ball.mp4'##'green_stuff.mp4'#'ball_tracking_example.mp4'#'orange_ball.mp4'#
buffer = 32
pts = deque(maxlen=buffer)
while (True):
    image = cap.read()[1]
    try:
        output = image.copy()
    except AttributeError:
        break
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detect circles in the image
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 75)
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)


    ###track ball
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "orange", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 4:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(output, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(output, center, 5, (0, 0, 255), -1)

    # update the points queue
    pts.appendleft(center)

    # loop over the set of tracked points
    for i in xrange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
        cv2.line(output, pts[i - 1], pts[i], (0, 0, 255), thickness)





    # show the output image
    cv2.imshow("output", output)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break