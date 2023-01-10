import cv2, math
from utils import singleton, Utils

@singleton
class Processor:

    DEBUG = False

    def __init__(self):
        self.utils = Utils()
        self.restart()
    
    def restart(self):
        self.__upper_barrier_counter__: int = 0
        self.__lower_barrier_counter__: int = 0
    
    def debug(self):
        # print("Processor debug")
        pass

    def __get_direction__(self, tracked_box: dict) -> float:
        '''
        Calculate the direction of the tracked box and return it.

        ### Parameters:
        - `tracked_box`: The tracked box to calculate the direction.

        ### Returns:
        - `direction`: The direction of the tracked box (positive if the box is moving to the up, negative if the box is moving to the down)
        - `pt`: The pt of the tracked box.
        - `pt2`: The pt2 of the tracked box.
        '''
        # Get the pt and pt2 of the tracked box
        pt = tracked_box.get('pt', None)
        pt2 = tracked_box.get('pt2', None)
        if (pt2[0], pt2[1]) == (-1, -1):
            return None, None, None
        # If the pt and pt2 are not None
        if pt is not None and pt2 is not None:
            # Get the direction
            direction = pt2[1] - pt[1]
            # Return the direction
            return direction, pt, pt2
        return None, None, None
    
    def process(self, tracked_boxes:list, barriers):
        '''
        Calculate the number of cars that are crossing the barriers.

        ### Parameters:
        - `tracked_boxes`: The list of tracked boxes.
        - `barriers`: The barriers.

        ### Returns:
        - `lower_barrier_counter`: The number of cars that are crossing the lower barrier (is going to the down).
        - `upper_barrier_counter`: The number of cars that are crossing the upper barrier (is going to the up).
        '''
        # Get the barriers
        lower_barrier, upper_barrier = barriers
        # For each tracked box, get the direction and the speed
        for tracked_box in tracked_boxes:
            # Get the direction
            direction, pt, pt2 = self.__get_direction__(tracked_box)
            # Check if the direction is not None
            if direction is not None:
                # Check if the tracked box is moving to the up
                if direction > 0:
                    # The object is moving to the up
                    # Check if the tracked box is crossing the upper barrier
                    if pt[1] <= upper_barrier <= pt2[1]:
                        if self.DEBUG:
                            print(f"The car is crossing the upper barrier: {pt} - {pt2}. Direction: {direction}, Upper barrier: {upper_barrier}")
                        # Add 1 to the counter of the upper barrier
                        self.__upper_barrier_counter__ += 1
                else:
                    # The object is moving to the down
                    # Check if the tracked object is crossing the lower barrier
                    if pt2[1] <= lower_barrier <= pt[1]:
                        if self.DEBUG:
                            print(f"The car is crossing the lower barrier: {pt[1]}({pt}) - {pt2[1]}({pt2}). Direction: {direction}, Lower barrier: {lower_barrier}")
                        # Add 1 to the counter of the lower barrier
                        self.__lower_barrier_counter__ += 1
        return self.__lower_barrier_counter__, self.__upper_barrier_counter__