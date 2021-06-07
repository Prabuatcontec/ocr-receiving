import os, shutil
import sys
import pytesseract
import cv2
import numpy as np
from PIL import Image
from flask import session
import json
import time
from modelunitvalidation import ModelValidation
from filehandling import HoldStatus
from scipy.ndimage import interpolation as inter
import time
from config import Config
import os.path
import requests
import pickle
import glob

ds_factor = 0.6

os.environ['OMP_THREAD_LIMIT'] = '2'
class ImageProcess(object):
    def readData(self):
        
        with open("static/uploads/_serial.txt", 'r') as t:
            num_lines = sum(1 for line in open("static/uploads/_serial.txt"))

            if(num_lines == ''):
                num_lines = 0

            if(num_lines==0):
                self.updateFile("0","_serialrowcount")
                self.updateFile("0","_processing")

            for i,line in enumerate(t):
                self.updateFile("1","_processing")
                line = self.trimValue(line)
                self.processImage(line)
                if(int(num_lines -1) == int(i)):
                    self.resetProcess()
                    

            return 1

    def trimValue(self, line):
        line = line.replace('"', '')         # i == n-1 for nth line
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.split(',')
        return line

    def updateFile(self, value, filename):  
        HoldStatus("").writeFile(value, filename)

    def processImage(self, line):
        if os.path.isfile("static/processingImg/boxER_"+line[0]+".jpg"):
                imName = line[0]
                image = cv2.imread("static/processingImg/boxER_"+line[0]+".jpg")
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(Image.fromarray(gray))
                validation = open("static/uploads/_validation.txt", 'r').read()
                strVal = str(validation)
                models = json.loads(strVal)
                self.processValidation(models, text, line, imName)

    def processValidation(self, models, text, line, imName):
        for key, value in models.items():
            if key.replace('"', "") in text:
                model = key
                valid = str(value).replace("'",'"')
                jsonArray =json.loads(str(valid))
                count = 0
                
                line.pop(0)
                valid = ModelValidation().validate(
                    jsonArray["data"], line)
                if valid == '0':
                    dict = {}
                    p = 0
                    for c in range(len(line)):
                        r = open("static/uploads/_goodData.txt", "r")
                        newline = line[c].replace("\n","")
                        newline = newline.replace(" ","")
                        
                        r = str(r.read())
                        if(r.find(newline) != -1):
                            p = 1
                            break
                        if(c == 0):
                            mdict1 = {"serial": newline}
                            dict.update(mdict1)
                            oldSerial = newline
                            if newline.strip() in r:
                                p = 1
                                break
                        else:
                            mdict1 = {str("address"+str(c)): newline}
                            dict.update(mdict1)
                            if newline.strip() in r:
                                p = 1
                                break

                    if(p == 0):
                        mdict1 = {"model": str(model)}
                        dict.update(mdict1)
                        
                        if(oldSerial in r):
                            break
                        else:
                            file1 = open("static/uploads/_goodData.txt", "a")
                            file1.write("\n")
                            file1.write(str(dict))
                            HoldStatus("").writeFile("1", "_scan")
                            data=json.dumps(dict)
                            shutil.copy("static/processingImg/boxER_"+imName+".jpg","static/s3Bucket/boxER_"+imName+".jpg")
                            self.resetProcess()
                            break
                else:
                    HoldStatus("").writeFile("0", "_scan")

                break
            elif key.replace('"', "") not in text:
                continue

    def resetProcess(self):
        for file in os.scandir("static/processingImg"):
            if file.name.endswith(".jpg"):
                os.unlink(file.path)
        HoldStatus("").writeFile("0", "_processing")
        HoldStatus("").writeFile("0", "_serialrowcount")
        HoldStatus("").writeFile("", "_serial")
        HoldStatus("").writeFile("", "_lastScan")
        HoldStatus("").writeFile("0", "_lastScanCount")

    def postToDeepblu(self):
        with open("static/uploads/_goodData.txt", 'r') as t:
            for i,line in enumerate(t):
                r = HoldStatus("").readFile("_serialpostCount")
                if(str(line) != "\n"):
                    if(int(r) < i):
                        
                        line = line.replace("'",'"')
                        response = requests.post(Config.DEEPBLU_URL + '/autoreceive/automation', line,
                                    headers={'Content-Type': 'application/json', 
                                    'Authorization': 'Basic QVVUT1JFQ0VJVkU6YXV0b0AxMjM=' }
                                    )
                        HoldStatus("").writeFile(str(i), "_serialpostCount")

    
    def calibrateIt(self):

        print(2)
 
        # Chessboard dimensions
        number_of_squares_X = 10 # Number of chessboard squares along the x-axis
        number_of_squares_Y = 7  # Number of chessboard squares along the y-axis
        nX = number_of_squares_X - 1 # Number of interior corners along x-axis
        nY = number_of_squares_Y - 1 # Number of interior corners along y-axis
        

        # Store vectors of 3D points for all chessboard images (world coordinate frame)
        object_points = []
        
        # Store vectors of 2D points for all chessboard images (camera coordinate frame)
        image_points = []
        
        # Set termination criteria. We stop either when an accuracy is reached or when
        # we have finished a certain number of iterations.
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Define real world coordinates for points in the 3D coordinate frame
        # Object points are (0,0,0), (1,0,0), (2,0,0) ...., (5,8,0)
        object_points_3D = np.zeros((nX * nY, 3), np.float32)       
        
        # These are the x and y coordinates                                              
        object_points_3D[:,:2] = np.mgrid[0:nY, 0:nX].T.reshape(-1, 2) 
        print(3339999999999999)
        images = glob.glob('static/calibration/*.jpg')
        
        for image_file in images:
            image = cv2.imread(image_file)

        #image = self.Zoom(image,2)
        img1 = image
        #image = cv2.imread('1622798624-214896_undistorted.jpg')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, jpeg = cv2.imencode('.jpg', image)

        # Find the corners on the chessboard
        success, corners = cv2.findChessboardCorners(gray, (nY, nX), None)
        
        images = glob.glob('static/calibration/*.jpg')

        print(9999999999999)    
          # Go through each chessboard image, one by one
        for image_file in images:
            print(image_file)
        
            # Load the image
            image = cv2.imread(image_file)  
        
            # Convert the image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
        
            # Find the corners on the chessboard
            success, corners = cv2.findChessboardCorners(gray, (nY, nX), None)
            
            # If the corners are found by the algorithm, draw them
            if success == True:
        
            # Append object points
                object_points.append(object_points_3D)
            
                # Find more exact corner pixels       
                corners_2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)       
                
                        # Append image points
                image_points.append(corners)
            
                # Draw the corners
                cv2.drawChessboardCorners(image, (nY, nX), corners_2, success)
        
            # Display the image. Used for testing.
            #cv2.imshow("Image", image) 
            
            # Display the window for a short period. Used for testing.
            #cv2.waitKey(200) 

        distorted_image = image

        # Perform camera calibration to return the camera matrix, distortion coefficients, rotation and translation vectors etc 
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(object_points, 
                                                            image_points, 
                                                            gray.shape[::-1], 
                                                            None, 
                                                            None)
        
        # Get the dimensions of the image 
        height, width = distorted_image.shape[:2]
            
        # Refine camera matrix
        # Returns optimal camera matrix and a rectangular region of interest
        optimal_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, 
                                                                    (width,height), 
                                                                    1, 
                                                                    (width,height))
        
        # Undistort the image 
        

        # Create the output file name by removing the '.jpg' part
        

        calib_result_pickle = {}
        calib_result_pickle["mtx"] = mtx
        calib_result_pickle["optimal_camera_matrix"] = optimal_camera_matrix
        calib_result_pickle["dist"] = dist
        calib_result_pickle["rvecs"] = rvecs
        calib_result_pickle["tvecs"] = tvecs
        pickle.dump(calib_result_pickle, open("static/uploads/camera_calib_pickle.p", "wb" )) 

        return calib_result_pickle

        
