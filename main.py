"""Offers Functions that sense specific gestures
Source: https://github.com/ishfulthinking/Python-Hand-Gesture-Recognition?tab=readme-ov-file"""
import numpy as np
import cv2
import config as c
from gesture_library import HandData, write_on_image, get_region, get_average, segment, get_hand_data
from spotify_function import start_stop_song

def main():
    # capture video
    capture = cv2.VideoCapture(1)
    while (True):
        #get current frame in image and flip to mirrorx
        ret, frame = capture.read()
        frame = cv2.resize(frame, (c.FRAME_WIDTH, c.FRAME_HEIGHT))
        frame = cv2.flip(frame,1)
        #get region and then average background
        region = get_region(frame)
        if c.frames_elasped < c.CALIBRATION_TIME:
            get_average(region)
        else:
            region_pair = segment(region)
            if region_pair is not None:
                # If region pair was found diplay them in another window
                threshholded_region, segmented_region = region_pair
                cv2.drawContours(region,[segmented_region], -1, (255,255,255))
                cv2.imshow("Segmented Image", region)

                get_hand_data(threshholded_region, segmented_region)
        #Spotipy Functions
        if c.hand is not None and c.frames_elasped % 50 == 0:
            if c.hand.fingers == c.SS_NUMBER:
                start_stop_song()
            elif c.hand.fingers == c.SKIP_NUMBER:
                pass

        #Annotate Current Frame
        write_on_image(frame,c.hand)
        #show current frame
        cv2.imshow("Camera Input", frame)
        c.frames_elasped += 1
        #Check if user wants to exit
        if (cv2.waitKey(1) & 0xFF == ord('x')):
            break
        #Recalibrate with r
        elif (cv2.waitKey(1) & 0xFF == ord('r')):
            c.frames_elasped = 0

    #Stop capture and delete window
    capture.release()
    cv2.destroyAllWindows

if __name__ == '__main__':
    main()