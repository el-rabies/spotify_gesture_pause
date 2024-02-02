"""Provides classes and functions for gesture sensing"""
import cv2
import numpy as np
import config as c
#Hand Class
class HandData:
    top = (0,0)
    bottom = (0,0)
    left = (0,0)
    right = (0,0)
    centerX = 0
    prevCenterX = 0
    isInFrame = False
    isWaving = False
    fingers = 0
    gesture_list = []

    def __init__(self, top, bottom, left, right, centerX):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.centerX = centerX
        self.prevCenterX = 0
        isInFrame = False
        isWaving = False
    
    def update(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
    
    def checkForWaving(self, centerX):
        self.prevCenterX = self.centerX
        self.centerX = centerX

        if abs(self.centerX - self.prevCenterX > 3):
            self.isWaving = True
        else:
            self.isWaving = False

def write_on_image(frame,hand):
    """Prints which gesture is being detected to screen"""
    text = "Searching..."

    if c.frames_elasped < c.CALIBRATION_TIME:
        text = "Calibrating..."
    elif hand == None or hand.isInFrame == False:
        text = "No hand detected"
    else:
        if hand.isWaving:
            text = "Waving"
        else:
            for i in range(5):
                if hand.fingers == i:
                    text = "Showing " + str(i) + " fingers"
    
    cv2.putText(frame, text, (10,20), cv2.FONT_HERSHEY_COMPLEX, 0.4,( 0 , 0 , 0 ),2,cv2.LINE_AA)
    cv2.putText(frame, text, (10,20), cv2.FONT_HERSHEY_COMPLEX, 0.4,(255,255,255),1,cv2.LINE_AA)
    cv2.rectangle(frame, (c.region_left, c.region_top), (c.region_right, c.region_bottom), (255,255,255), 2)

def get_region(frame):
    """Gets the region of interest and saves it to a cv2 image object"""
    #Separate Region of interest
    region = frame[c.region_top:c.region_bottom, c.region_left:c.region_right]
    #Convert Region to grayscale
    region = cv2.cvtColor(region,cv2.COLOR_BGR2GRAY)
    #Gaussian Blur to remove noise
    region = cv2.convertScaleAbs(region, alpha=c.ALPHA, beta=c.BETA)
    region = cv2.GaussianBlur(region, (5,5), 0)
    return region

def get_average(region):
    """Get the average of the background while calibrating"""
    #if we havent set the background yet then set it
    if c.background is None:
        c.background = region.copy().astype("float")
        return
    #otherwise add captured frame to the average of the background
    cv2.accumulateWeighted(region,c.background,c.BG_WEIGHT)

def segment(region):
    """Find the diffrent between the background found at calibration and the current frame"""
    #find the diffrence between the background and the current frame
    diff = cv2.absdiff(c.background.astype(np.uint8), region)
    #threshhold the region to get a BW only image
    thresholded_region = cv2.threshold(diff, c.OBJ_TRESHHOLD, 255, cv2.THRESH_BINARY)[1]
    #get the countours of the region which returns the outline of the hand
    contours = cv2.findContours(thresholded_region.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #If we got nothing theres no hand
    if len(contours[0]) == 0:
        if c.hand is not None:
            c.hand.isInFrame = False
        return
    #Otherwise return a tuple of the filled hand and outline
    else:
        if c.hand is not None:
            c.hand.isInFrame = True
        segmented_region = max(contours[0], key = cv2.contourArea)
        return(thresholded_region, segmented_region)
    
def get_hand_data(thresholded_image, segmented_image):
    """Gets the data of the hand currently in frame"""
    #Enclose the area around the fingies in a convex hull to connect all the bits
    convexHull = cv2.convexHull(segmented_image)
    #Find extremities of convext hull and label them as points
    top    = tuple(convexHull[convexHull[:, :, 1].argmin()][0])
    bottom = tuple(convexHull[convexHull[:, :, 1].argmax()][0])
    left   = tuple(convexHull[convexHull[:, :, 0].argmin()][0])
    right  = tuple(convexHull[convexHull[:, :, 0].argmax()][0])
    #Get the centre of the palm
    centreX = int((left[0] + right[0]) / 2)
    #Create or update hand
    if c.hand == None:
        c.hand =HandData(top, bottom, left, right, centreX)
    else:
        c.hand.update(top, bottom, left, right)
    #check for waving
    if c.frames_elasped % 8 == 0:
        c.hand.checkForWaving(centreX)
    #get the number of fingers
    c.hand.fingers = count_fingers(thresholded_image)

    #get most frequence gesture every 12 frames then clear
    c.hand.gesture_list.append(count_fingers(thresholded_image))
    if c.frames_elasped % 12 == 0:
        c.hand.fingers = most_frequent(c.hand.gesture_list)
        c.hand.gesture_list.clear()

def count_fingers(thresholded_image):
    """Counts the number of fingers on the hand currently in frame"""
    #Find height at which we will draw fingers
    line_height = int(c.hand.top[1] + (0.2 * (c.hand.bottom[1] - c.hand.top[1])))

    #get linear region of intrest where fingers should be
    line = np.zeros(thresholded_image.shape[:2], dtype=int)

    #draw line across region of intrest
    cv2.line(line, (thresholded_image.shape[1], line_height), (0,line_height), 255, 1)

    #Find where the line intersects the hand with bitwise AND (this is where the fingers are)
    line = cv2.bitwise_and(thresholded_image, thresholded_image, mask=line.astype(np.uint8))

    #get the lines new contours
    contours = cv2.findContours(line.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    #count the number of fingers
    fingers = 0
    for curr in contours[0]:
        width = len(curr)
        if width < 3 * abs(c.hand.right[0] - c.hand.left[0]) / 4 and width > 5:
            fingers += 1
    
    return fingers

def most_frequent(input_list):
    """Gets the most frequent gesture"""
    #get most frequent gesture
    dict = {}
    count = 0
    most_freq = 0

    for item in reversed(input_list):
        dict[item] = dict.get(item, 0) +1
        if dict[item] >= count :
            count, most_freq = dict[item], item
    
    return most_freq