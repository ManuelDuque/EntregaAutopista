import cv2, math
from utils import singleton, Utils

@singleton
class ObjectDetector:

    DEBUG = False
    PAUSED_DEBUG = False
    
    def __init__(self):
        self.utils = Utils()
        self.__object_detector__ = cv2.createBackgroundSubtractorMOG2(varThreshold=30)
        self.__kernel__ = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.restart()
    
    def debug(self):
        '''
        Process the debug information.
        '''
        self.__start_debug__(self.__last_frame__)

    def __start_debug__(self, frame):
        if frame is not None:
            # Draw the boxes on the frame
            for box in self.__boxes__:
                x, y, w, h, center = box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, center, 2, (0, 0, 255), 2)
            # Show the frame
            cv2.imshow('Frame', frame)
            # Show the mask
            cv2.imshow('Mask', self.__mask__)
            # Show the threshold
            cv2.imshow('Threshold', self.__threshold__)
            # Show the closing
            cv2.imshow('Closing', self.__closing__)
            # Show the opening
            cv2.imshow('Opening', self.__opening__)
            # Show the dilation
            cv2.imshow('Dilation', self.__dilation__)
            # Apply a stop
            if self.PAUSED_DEBUG:
                cv2.waitKey(0)

    def restart(self):
        self.__boxes__ = []
        self.__last_frame__ = None

    def __get_boxes__(self, frame):
        # Save the frame
        self.__last_frame__ = frame.copy()
        # Convert to grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply the object detector to the frame
        self.__mask__ = self.__object_detector__.apply(frame)
        # Apply a morphological closing to the mask
        self.__closing__ = cv2.morphologyEx(self.__mask__, cv2.MORPH_CLOSE, self.__kernel__)
        # Apply a morphological opening to the mask
        self.__opening__ = cv2.morphologyEx(self.__closing__, cv2.MORPH_OPEN, self.__kernel__)
        # Apply a dilation
        self.__dilation__ = cv2.dilate(self.__opening__, self.__kernel__, iterations=2)
        # Apply a threshold to the mask
        _, self.__threshold__ = cv2.threshold(self.__dilation__, 220, 255, cv2.THRESH_BINARY)
        # Find the contours
        contours, hierarchy = cv2.findContours(self.__threshold__, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Sort the contours by area (descending)
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        # Filter the contours by hierarchy (remove the ones that are inside other contours)
        filtered_contours = []
        for i, c in enumerate(sorted_contours):
            if hierarchy[0][i][3] == -1:
                filtered_contours.append(c)
        # Filter the contours by area (remove the small ones)
        filtered_contours = [c for c in filtered_contours if 150 < cv2.contourArea(c) < 20000]
        # Get the bounding boxes
        bounding_boxes = [cv2.boundingRect(c) for c in filtered_contours]
        # Add the center of the bounding box to the list
        return_boxes = []
        for box in bounding_boxes:
            x, y, w, h = box
            center = (x + w // 2, y + h // 2)
            return_boxes.append([x, y, w, h, center])
        # Return the list of bounding boxes
        return return_boxes

    def detect(self, frame) -> list:
        '''
        Detects objects in the frame and returns a list of boxes with the format [x, y, w, h].

        ### Parameters:
        - `frame`: The frame to detect objects in.

        ### Returns:
        - `list`: A list of boxes with the format [x, y, w, h, center].
        '''
        # Create a copy of the frame
        frame_copy = frame.copy()
        # Get the boxes
        self.__boxes__ = self.__get_boxes__(frame_copy)
        # Debug
        if self.DEBUG:
            self.__start_debug__(frame)
        # Return the list of boxes
        return self.__boxes__