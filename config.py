"""Global Variables"""
#Hold background frame
background = None
#Hold hand data
hand = None
#count frames and set size of window
frames_elasped = 0
FRAME_HEIGHT = 200
FRAME_WIDTH = 300

#Spotify Authorization Stuff (CHANGE THIS)
CLIENT_ID = "Your Client ID"
CLIENT_SECRET = "Your Secret ID"
REDIRECT_URI = 'http://localhost:3000/callback'
SCOPEs = ['app-remote-control', 'user-read-playback-state', 'user-modify-playback-state']

#Settings (CHANGE THESE)
SS_NUMBER = 3 #Number of fingers bound to the start/stop action
SKIP_NUMBER = 0 #Number of fingers bound to the skip action
CALIBRATION_TIME = 30 #Time to calibrate
BG_WEIGHT = 0.2 
OBJ_TRESHHOLD = 15
ALPHA = 1.2 #Contrast
BETA = 10 #Brightness

#Get scanning region
region_top = 0 
region_bottom = int(2 * FRAME_HEIGHT / 3)
region_left = int(FRAME_WIDTH / 2)
region_right = FRAME_WIDTH
