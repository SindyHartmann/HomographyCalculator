import numpy as np
import cv2
import numpy as np
from PIL import Image
#from scikit-i.transform import ProjectiveTransform


class Homography:
    cornersField = None
    imageField = []
    homography = []
    def __init__(self):
        self.cornersField = np.asarray([[0, 0], [0, 2000], [2000, 2000], [2000, 0], [4000, 0], [4000, 2000]])


    def calcHomography(self, imagePoints, pointIndices):

        imagePoints = np.asarray(imagePoints, dtype = "float32")
        print(imagePoints)
        if len(pointIndices) < 3:
            return -1
        modIndices = list([s % 2 for s in pointIndices])
        if(modIndices.count(1)==0 or modIndices.count(0)==0):
            return -2
        dstPoints= np.asarray(self.cornersField[np.asarray(pointIndices)], dtype = "float32")
        print(dstPoints)
        print(np.float32(dstPoints))
        #M = cv2.getPerspectiveTransform(imagePoints, dstPoints)
        #self.homography = M
        #print(M)
        #t = ProjectiveTransform()
        #self.homography = t.estimate(imagePoints,dstPoints)
        self.homography, mask = cv2.findHomography(np.float32(imagePoints), np.float32(dstPoints))
        return 1



    def transformPoint(self, point):
        if len(self.homography)>0:
            return cv2.perspectiveTransform(point, self.homography)
        else:
            return None

    def transformImage(self, image):
        if len(self.homography)>0:
            print(self.homography)
            image = np.array(image)
            x,y,z = image.shape

            imageTransformed = cv2.warpPerspective(image, self.homography, (7*y,7*x))
            return Image.fromarray(imageTransformed)
        else:
            return None