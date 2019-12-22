from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO
#from time import sleep

GPIO.setmode(GPIO.BOARD)
Motor1A = 16
Motor1B = 18
Motor1E = 22
 
Motor2A = 23
Motor2B = 21
Motor2E = 19

GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)

GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)
GPIO.setup(Motor2E,GPIO.OUT)



camera =  PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
rawCapture = PiRGBArray(camera,size=(640,480))

time.sleep(0.5)

for frame in camera.capture_continuous(rawCapture,format="bgr",use_video_port=True):
    
    image = frame.array
    frame = image
    
    eye_detect = cv2.CascadeClassifier('/home/pi/Desktop/minor_project/eye_detect.xml')  
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    eyes = eye_detect.detectMultiScale(gray)
    
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(frame, (ex,ey), ((ex+ew),(ey+eh)), (0,0,255),2)
        crop = frame[ey:(ey+eh), ex:(ex+ew)]
        a = eh*ew
        if 5000 < a < 18000:
            image = cv2.equalizeHist(gray[ey:(ey+eh), ex:(ex+ew)])
            frame = image
        #print(eh*ew)
            ret, image = cv2.threshold(image,55,255,cv2.THRESH_BINARY)		#50
        
            threshold = cv2.inRange(image,250,255)
         
            _,contours, hierarchy = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        
            #print(len(contours))
            
            if len(contours) >= 2:
                          				#find biggest blob
                maxArea = 0
                MAindex = 0			#to get the unwanted frame 
                distanceX = []		#delete the left most (for right eye)
                currentIndex = 0
              
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    center = cv2.moments(cnt)
                  
                    if center['m00'] != 0:
                        cx = int(center["m10"] / center["m00"])
                        cy = int(center["m01"] / center["m00"])
                    else:
                        cx,cy = 0, 0
                  
                    distanceX.append(cx)	
                    if area > maxArea:
                        maxArea = area
                        MAindex = currentIndex
                     
                    currentIndex = currentIndex + 1
                 
                del contours[MAindex]		#remove the picture frame contour
                del distanceX[MAindex]
         
            eye = 'right'
         
            if len(contours) >= 2:
             #delete the left most blob for right eye
                if eye == 'right':
                    edgeOfEye = distanceX.index(min(distanceX))
                else:
                    edgeOfEye = distanceX.index(max(distanceX))	
                del contours[edgeOfEye]
                del distanceX[edgeOfEye]
         
            if len(contours) >= 1:		#get largest blob
                maxArea = 0
                for cnt in contours:
                 
                    area = cv2.contourArea(cnt)
                    if area > maxArea:
                        maxArea = area
                        largeBlob = cnt
        
            if len(largeBlob) > 0:
            
                center = cv2.moments(largeBlob)
                #cx,cy = int(center['m10']/center['m00']), int(center['m01']/center['m00'])
                if center['m00'] != 0:
                    cx = int(center["m10"] / center["m00"])
                    cy = int(center["m01"] / center["m00"])
                else:
                    cx,cy = 0, 0
                cv2.circle(frame,(cx,cy),5,255,-1)
            
            #print(ex,ey,ex+ew,ex+ey)
            #print(cx,cy)
            #print("*******************************")
            
            #***middle**
            if 40 < cx < 60:
                print("middle")
                print("*******************************")
                GPIO.output(Motor1A,GPIO.HIGH)
                GPIO.output(Motor1B,GPIO.LOW)
                GPIO.output(Motor1E,GPIO.HIGH)
 
                GPIO.output(Motor2A,GPIO.HIGH)
                GPIO.output(Motor2B,GPIO.LOW)
                GPIO.output(Motor2E,GPIO.HIGH)
            elif 70 < cx < 90:
                print("LEFT")
                print("*******************************")
                GPIO.output(Motor1A,GPIO.HIGH)
                GPIO.output(Motor1B,GPIO.LOW)
                GPIO.output(Motor1E,GPIO.HIGH)
 
                GPIO.output(Motor2A,GPIO.LOW)
                GPIO.output(Motor2B,GPIO.HIGH)
                GPIO.output(Motor2E,GPIO.HIGH)
                
            elif 1 < cx < 20:
                print("RIGHT")
                print("*******************************")
                GPIO.output(Motor1A,GPIO.LOW)
                GPIO.output(Motor1B,GPIO.HIGH)
                GPIO.output(Motor1E,GPIO.HIGH)
 
                GPIO.output(Motor2A,GPIO.HIGH)
                GPIO.output(Motor2B,GPIO.LOW)
                GPIO.output(Motor2E,GPIO.HIGH)
                
                
            elif 25 < cy < 40:
                print("UP")
                print("*******************************")
                GPIO.output(Motor1A,GPIO.HIGH)
                GPIO.output(Motor1B,GPIO.LOW)
                GPIO.output(Motor1E,GPIO.HIGH)
 
                GPIO.output(Motor2A,GPIO.HIGH)
                GPIO.output(Motor2B,GPIO.LOW)
                GPIO.output(Motor2E,GPIO.HIGH)
                


    
    cv2.imshow("show",frame)
    #cv2.imshow("crop",crop)
        
    
    key = cv2.waitKey(1) & 0xFF
    
    rawCapture.truncate(0)
    
    if key == ord("q"):
        break
