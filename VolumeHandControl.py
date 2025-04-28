import cv2
import time
import numpy as np
import math
import HandTrackingModule as htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480
pTime=0
cTime=0

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)

detector=htm.handDetector(detectionCon=0.8)

# Volume Handler
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange=volume.GetVolumeRange()
minVol=volRange[0]
maxVol=volRange[1]
vol=0
volBar=400
volPer=0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)
    if(len(lmList)!=0):

        # Getting Thumb(x1,y1) and Second Finger(x2,y2) Position
        x1,y1 = lmList[4][1],lmList[4][2]
        x2,y2 = lmList[8][1],lmList[8][2]
        # Middle Position between Two fingers
        cx,cy = (x1+x2)//2,(y1+y2)//2

        # Drawing Circles and Line between fingers
        cv2.circle(img,(x1,y1),10,(255, 0, 180),cv2.FILLED)
        cv2.circle(img,(x2,y2),10,(255, 0, 180),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255, 0, 180),3)
        cv2.circle(img,(cx,cy),10,(255, 0, 180),cv2.FILLED)

        length = math.hypot(x2-x1,y2-y1)

        # Hand Length = 50 - 300
        # Volume = -65 - 0
        vol = np.interp(length,[50,180],[minVol,maxVol])
        volBar = np.interp(length,[50,180],[400,150])
        volPer = np.interp(length,[50,180],[0,100])
        volume.SetMasterVolumeLevel(vol, None)
        print(vol)

        if(length<50):
            cv2.circle(img, (cx,cy), 10, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img,(50,150),(85,400),(255,0,0),3)
        cv2.rectangle(img,(50,int(volBar)),(85,400),(255,0,0),cv2.FILLED)
        cv2.putText(img,f'{int(volPer)} %',(40,450),cv2.FONT_HERSHEY_PLAIN,2,(255,0,0),2)

    # FPS Working
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(img,f'FPS: {int(fps)}',(30,50),cv2.FONT_HERSHEY_PLAIN,2,(255,0,0),2)

    cv2.imshow("Img",img)
    cv2.waitKey(1)
