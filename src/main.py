'''
Example of a simple program that process a video and track each car in the video counting the number of cars that pass through barriers.

Call the program as follows:
python ./src/main.py <video_file>

The program uses the following classes:
- VideoProcessor: to process the video
- CarTracker: to track the cars
- CarCounter: to count the cars
- Car: to represent a car
'''
import sys
from PyQt5.QtWidgets import QApplication
from ui import Window

if __name__ == "__main__":
    video_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = QApplication(sys.argv)
    window = Window(video_file)
    app.exec_()
    sys.exit(0)