from utils import singleton, Utils
from PyQt5 import uic, QtCore, QtGui
import cv2, numpy as np
from detector import ObjectDetector
from tracker import Tracker
from processor import Processor

@singleton
class Window:
    '''
    Class to create the window of the application and manage the events.
    '''

    def __init__(self, video_file: str=None):
        '''
        Constructor of the class.
        '''
        # Load the utils
        self.utils = Utils()
        # Load the object detector
        self.object_detector = ObjectDetector()
        # Load the object tracker
        self.object_tracker = Tracker()
        # Load the processor
        self.processor = Processor()
        # Load the config file
        self.ui_config = self.utils.loadJson("src/config/ui_config.json")
        # Save the video file
        self.video_file = video_file if video_file is not None else self.utils.getValueOf(self.ui_config, "video", "video_file_path")
        # Load the ui
        relative_path = self.utils.getValueOf(self.ui_config, "ui", "ui_file_path")
        if relative_path is None:
            raise Exception("The ui file path is not defined in the config file.")
        self.ui = uic.loadUi( self.utils.getAbsolutePath( relative_path ) )
        # Set the title of the window
        title = self.utils.getValueOf(self.ui_config, "ui", "title")
        title = title if title is not None else "Title not defined"
        self.ui.setWindowTitle(title)
        # Create the timer
        self.timer = QtCore.QTimer(self.ui)
        # Setup the connections
        self.__setup_connections__()
        # Reset the variables
        self.__restart__()
        # Set the debug mode
        self.__debug_mode__ = False
        # Start the window
        self.ui.show()
    
    def __setup_connections__(self) -> None:
        '''
        ### Private method.
        Setup the connections of the buttons and the spin box.

        ### Parameters:
        - No parameters.

        ### Returns
        - `None`: No returns.
        '''
        # Set the connections of the speed buttons
        self.ui.spinSpeed.valueChanged.connect(self.__speedButton__)
        # Set the connections of the buttons debug
        self.ui.buttonDebug.clicked.connect(self.__startDebug__)
        self.ui.buttonCloseDebug.clicked.connect(self.__stopDebug__)
        # Set the connections of the pause and restart buttons
        self.ui.buttonPause.clicked.connect(self.__pauseButton__)
        self.ui.buttonRestart.clicked.connect(self.__restart__)
        # Set the barriers connections of the buttons
        self.ui.sliderBarrera2.valueChanged.connect(self.__on_change_upper_barrier__)
        self.ui.spinBarrera2.valueChanged.connect(self.__on_change_upper_barrier__)
        self.ui.sliderBarrera1.valueChanged.connect(self.__on_change_lower_barrier__)
        self.ui.spinBarrera1.valueChanged.connect(self.__on_change_lower_barrier__)
        # Set the timer to the update function
        self.timer.timeout.connect(self.__update__)
        return None
    
    def __update_counters__(self, counter_lower, counter_upper) -> None:
        '''
        ### Private method.
        Update the counters of the cars in the ui.

        ### Parameters:
        - `counter_lower`: The number of cars that pass through the lower barrier.
        - `counter_upper`: The number of cars that pass through the upper barrier.
        '''
        counter_text_one: str = self.utils.getValueOf(self.ui_config, "ui", "counter_text1")
        counter_text_two: str = self.utils.getValueOf(self.ui_config, "ui", "counter_text2")
        self.ui.counter1.setText(counter_text_one.format(str(counter_upper)))
        self.ui.counter2.setText(counter_text_two.format(str(counter_lower)))
        return None
    
    def __restart__(self) -> None:
        '''
        ### Private method.
        Restart the variables of the application.

        ### Parameters:
        - No parameters.

        ### Returns:
        - `None`: No returns.
        '''
        # Call to restart the other modules
        self.object_detector.restart()
        self.object_tracker.restart()
        self.processor.restart()
        # Set the last frame to None
        self.__last_frame__ = None
        # Set the default values of the counters
        self.__update_counters__(0, 0)
        # Get the FPS defined in the config file
        fps = self.utils.getValueOf(self.ui_config, "video", "fps")
        fps = fps if fps is not None else 60
        # Set the default FPS to the spin box
        self.ui.spinSpeed.setValue(fps)
        # Set the default values of the barriers
        lower_barrier = self.utils.getValueOf(self.ui_config, "barriers", "lower")
        upper_barrier = self.utils.getValueOf(self.ui_config, "barriers", "upper")
        if lower_barrier is None or upper_barrier is None:
            raise Exception("The barriers are not defined in the config file.")
        # Set the default values of the lower barrier
        self.__setup_default_barriers__()
        # Save the video
        self.video = cv2.VideoCapture( self.utils.getAbsolutePath( self.video_file ) )
        # Save the total number of frames
        self.__video_total_frames__ = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        # Save the FPS of the video
        self.__video_fps__ = int(self.video.get(cv2.CAP_PROP_FPS))
        # Save the width and the height of the video
        self.__video_width__ = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.__video_height__ = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Set the timer to the FPS
        self.__speedButton__()
    
    def __setup_default_barriers__(self, lower_barrier_y=None, upper_barrier_y=None) -> None:
        '''
        ### Private method.
        Set the default barriers values.

        ### Parameters:
        - lower_barrier_y: The y value of the lower barrier.
        - upper_barrier_y: The y value of the upper barrier.

        ### Returns:
        None

        ### Rules:
        - The lower barrier value can't be greater than the upper barrier value.
        - The upper barrier value can't be lower than the lower barrier value.
        - The barriers values can't be greater than 99.
        '''
        if lower_barrier_y is not None and upper_barrier_y is not None:
            if lower_barrier_y > upper_barrier_y:
                lower_barrier_y, upper_barrier_y = upper_barrier_y, lower_barrier_y
            self.__on_change_upper_barrier__(
                upper_barrier_y,
                self.utils.getValueOf(self.ui_config, "barriers", "upper", "color"),
                self.utils.getValueOf(self.ui_config, "barriers", "upper", "thickness")
            )
            self.__on_change_lower_barrier__(
                lower_barrier_y,
                self.utils.getValueOf(self.ui_config, "barriers", "lower", "color"),
                self.utils.getValueOf(self.ui_config, "barriers", "lower", "thickness")
            )
        else:
            default_lower = self.utils.getValueOf(self.ui_config, "barriers", "lower", "y")
            default_upper = self.utils.getValueOf(self.ui_config, "barriers", "upper", "y")
            self.__setup_default_barriers__(default_lower, default_upper)
        return None

    def __on_change_lower_barrier__(self, lower, color=None, thickness=None) -> None:
        '''
        ### Private method.
        Allow to change the lower barrier value.

        ### Parameters:
        - lower: The new lower barrier value.
        - color: The new color of the lower barrier.
        - thickness: The new thickness of the lower barrier.

        ### Returns:
        None

        ### Rules:
        - The lower barrier value can't be greater than the upper barrier value.
        '''
        if lower is None:
            return
        upper = self.ui.spinBarrera2.value()
        lower = lower if lower <= upper else upper
        self.ui.spinBarrera1.setValue(lower)
        self.ui.sliderBarrera1.setValue(lower)
        self.__lower_barrier__ = { "y": lower, "color": color if color is not None else [255, 0, 0], "thickness": thickness if thickness is not None else 5 }
        # Draw the last frame with the new barriers
        if self.__last_frame__ is not None:
            frame = self.__last_frame__.copy()
            frame = self.__draw_barriers__(frame)
            self.__set_image_to_view_source__(frame)
        return None

    def __on_change_upper_barrier__(self, upper, color=None, thickness=None) -> None:
        '''
        ### Private method.
        Allow to change the upper barrier value.

        ### Parameters:
        - upper: The new upper barrier value.
        - color: The new color of the upper barrier.
        - thickness: The new thickness of the upper barrier.
        
        ### Returns:
        None

        ### Rules:
        - The upper barrier value can't be lower than the lower barrier value.
        '''
        if upper is None:
            return
        lower = self.ui.spinBarrera1.value()
        upper = upper if upper >= lower else lower
        self.ui.spinBarrera2.setValue(upper)
        self.ui.sliderBarrera2.setValue(upper)
        self.__upper_barrier__ = { "y": upper, "color": color if color is not None else [0, 255, 0], "thickness": thickness if thickness is not None else 5 }
        # Draw the last frame with the new barriers
        if self.__last_frame__ is not None:
            frame = self.__last_frame__.copy()
            frame = self.__draw_barriers__(frame)
            self.__set_image_to_view_source__(frame)
        return None

    def __speedButton__(self):
        '''
        ### Private method.
        Allow to change the speed of the video.

        ### Parameters:
        - No parameters.

        ### Returns:
        - `None`: No return.

        ### Rules:
        - The speed can't be greater than the max speed value defined in the config file. If the max speed value is not defined, the max speed value will be 99.
        '''
        speed = self.ui.spinSpeed.value()
        max_speed = self.utils.getValueOf(self.ui_config, "MAX_SPEED")
        max_speed = max_speed if max_speed is not None else 99
        if speed == 0:
            self.timer.stop()
        else:
            speed = max_speed - speed
            self.timer.start(speed)
    
    def __startDebug__(self):
        '''
        ### Private method.
        Allow to show all the windows.

        ### Parameters:
        - No parameters.

        ### Returns:
        - `None`: No returns.
        '''
        self.__debug_mode__ = True
        self.object_detector.debug()
        self.object_tracker.debug()
        self.processor.debug()
    
    def __stopDebug__(self):
        '''
        ### Private method.
        Allow to hide all the windows.

        ### Parameters:
        - No parameters.

        ### Returns:
        - `None`: No returns.
        '''
        self.__debug_mode__ = False
        cv2.destroyAllWindows()

    def __pauseButton__(self):
        '''
        ### Private method.
        Allow to pause the video.

        ### Parameters:
        - No parameters

        ### Returns:
        - `None`: Nothing.
        '''
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.__speedButton__()
    
    def __update__(self):
        ret, frame = self.video.read()
        if ret:
            # Adapt the frame to the view_source size
            frame = self.__adapt_to_view_source__(frame)

            # Detect all the boxes in the frame
            boxes = self.object_detector.detect(frame)
            
            # Save the frame processed
            self.__last_frame__ = frame.copy()

            # Draw the barriers
            frame = self.__draw_barriers__(frame)
            
            # Track the boxes
            tracked_boxes: list = self.object_tracker.track(frame, boxes)

            # Process the tracked boxes
            down_counter, up_counter = self.processor.process(tracked_boxes, barriers=self.__calculate_position_barriers__(frame))

            # Update the counters
            self.__update_counters__(down_counter, up_counter)
            
            # Assign the frame to the view_source
            self.__set_image_to_view_source__(frame)

            if self.__debug_mode__:
                self.object_detector.debug()
                self.object_tracker.debug()
                self.processor.debug()

        else:
            self.video.release()
            cv2.destroyAllWindows()
            self.timer.stop()
    
    def __set_image_to_view_source__(self, image:np.ndarray=None) -> None:
        '''
        Set the image to the view_source window.

        ### Parameters:
        - `image`: The image to set.

        ### Returns:
        None
        '''
        if image is None:
            return
        # Get the pixmap from the image and show it
        pixmap = QtGui.QPixmap(QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format.Format_RGB888))
        # Show the image in the video_source window
        self.ui.video_source.setPixmap(pixmap)

    def __adapt_to_view_source__(self, frame) -> np.ndarray:
        '''
        ### Private method.
        Adapt the frame to the view_source size.

        ### Parameters:
        - `frame`: The frame to adapt.

        ### Returns:
        - `image`: The frame adapted to the view_source size.
        '''
        if frame is None:
            return None
        # Get width and height of the video_source window
        width = self.ui.video_source.width()
        height = self.ui.video_source.height()
        # Resize the frame
        image = cv2.resize(frame, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
        return image
    
    def __calculate_position_barriers__(self, image) -> tuple:
        '''
        Calculate the position of the barriers in the image.

        ### Parameters:
        - `image`: The image to calculate the barriers.

        ### Returns:
        - `lower_barrier`: The position of the lower barrier.
        - `upper_barrier`: The position of the upper barrier.
        '''
        # Get the width and height of the image
        height = image.shape[0]
        # Get the barriers from the ui position of y (0 to 100)
        lower_barrier = self.ui.sliderBarrera1.value()
        upper_barrier = self.ui.sliderBarrera2.value()
        # Invert the barriers
        lower_barrier = 100 - lower_barrier
        upper_barrier = 100 - upper_barrier
        # Calculate the real position of the barriers
        lower_barrier = int(lower_barrier * height / 100)
        upper_barrier = int(upper_barrier * height / 100)
        # Save the barriers
        self.__barriers__ = (lower_barrier, upper_barrier)
        # Return the barriers
        return (lower_barrier, upper_barrier)

    def __draw_barriers__(self, frame) -> np.ndarray:
        '''
        Draw the barriers in the image.

        ### Parameters:
        - `frame`: The image to draw the barriers.

        ### Returns:
        - `ndarray`: The image with the barriers.
        '''
        if frame is None:
            return None
        # Get the barriers
        lower_barrier, upper_barrier = self.__calculate_position_barriers__(frame)
        # Get the colors and thickness of the barriers
        lower_barrier_color = self.__lower_barrier__["color"]
        upper_barrier_color = self.__upper_barrier__["color"]
        lower_barrier_thickness = self.__lower_barrier__["thickness"]
        upper_barrier_thickness = self.__upper_barrier__["thickness"]
        # Draw the lower barrier
        y = lower_barrier
        point1 = (0, y)
        point2 = (frame.shape[1], y)
        cv2.line(frame, pt1=point1, pt2=point2, color=lower_barrier_color, thickness=lower_barrier_thickness)
        # Draw the upper barrier
        y = upper_barrier
        point1 = (0, y)
        point2 = (frame.shape[1], y)
        cv2.line(frame, pt1=point1, pt2=point2, color=upper_barrier_color, thickness=upper_barrier_thickness)
        return frame