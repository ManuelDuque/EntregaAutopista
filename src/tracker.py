import cv2, math
from utils import singleton, Utils

@singleton
class Tracker:

    DEBUG = False

    def __init__(self):
        self.utils = Utils()
        self.restart()
    
    def restart(self):
        self.__distance_threshold__ = 20
        self.__frame_count__: int = 0
        self.__center_points_previous_frame__: list = []
        self.__tracking_objects__: dict = {}
        self.__tracking_index__: int = 0
    
    def debug(self):
        # print("Tracker debug")
        pass

    def __start_debug__(self, frame):
        # Draw the boxes on the frame
        for object_id, pt in self.__tracking_objects__.items():
            cv2.circle(frame, pt, 2, (0, 0, 255), 2)
            cv2.putText(frame, str(object_id), (pt[0], pt[1] + 5), 0, 1, (0, 0, 255), 2)
        # Show the frame
        cv2.imshow('Frame', frame)
    
    def track(self, frame, boxes) -> list:
        '''
        Return a list of cars that are in the frame with the format [car_id, x, y, w, h, center].

        ### Parameters:
        - `frame`: The frame to process.
        - `boxes`: The list of boxes to track.
        
        ### Returns:
        - `cars`: The list of cars that are in the frame.
        '''
        self.__frame_count__ += 1
        
        # Get the center points of the boxes
        center_points_current_frame = [box[4] for box in boxes]
        
        if self.DEBUG:
            for pt in center_points_current_frame:
                cv2.circle(frame, pt, 2, (0, 0, 255), 2)

        previous_tracking_objects = self.__tracking_objects__.copy()
        
        # If it is the first frame, add all the center points to the tracking objects
        if self.__frame_count__ <= 2:
            for pt in center_points_current_frame:
                for pt2 in self.__center_points_previous_frame__:
                    distance = math.sqrt((pt[0] - pt2[0]) ** 2 + (pt[1] - pt2[1]) ** 2)
                    if distance < self.__distance_threshold__:
                        self.__tracking_objects__[self.__tracking_index__] = pt
                        previous_tracking_objects[self.__tracking_index__] = pt2
                        self.__tracking_index__ += 1
        else:
            tracking_objects = self.__tracking_objects__.copy()
            center_points_current_frame_copy = center_points_current_frame.copy()
            for object_id, pt2 in tracking_objects.items():
                object_exists = False
                for pt in center_points_current_frame_copy:
                    # Calculate the distance between the current point and the previous point
                    distance = math.sqrt((pt[0] - pt2[0]) ** 2 + (pt[1] - pt2[1]) ** 2)
                    # Update the tracking object position
                    if distance < self.__distance_threshold__:
                        self.__tracking_objects__[object_id] = pt
                        previous_tracking_objects[object_id] = pt2
                        object_exists = True
                        if pt in center_points_current_frame:
                            center_points_current_frame.remove(pt)
                        continue
                # Remove the tracking object if it does not exist anymore
                if not object_exists:
                    self.__tracking_objects__.pop(object_id)
            # Add the news tracking objects
            for pt in center_points_current_frame:
                self.__tracking_objects__[self.__tracking_index__] = pt
                previous_tracking_objects[self.__tracking_index__] = (-1, -1)
                self.__tracking_index__ += 1

        # Set a copy of the center points of the previous frame
        self.__center_points_previous_frame__ = center_points_current_frame.copy()

        if self.DEBUG:
            self.__start_debug__(frame)

        # Return the list of cars and their directions in the frame
        return [{"id": object_id, "pt": pt, "pt2": previous_tracking_objects[object_id]} for object_id, pt in self.__tracking_objects__.items()]