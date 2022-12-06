import cv2
from gaze_tracking import GazeTracking


class GazeTracker:
    def __init__(self):
        self.x_data = []
        self.y_data = []
        self.gaze = GazeTracking()

    async def add_frame(self, frame):
        self.gaze.refresh(frame)
        # frame = self.gaze.annotated_frame()
        text = ""

        if self.gaze.is_blinking():
            text = "Blinking"
        elif self.gaze.is_right():
            text = "Looking right"
        elif self.gaze.is_left():
            text = "Looking left"
        elif self.gaze.is_center():
            text = "Looking center"
        print(text)

        left_pupil = self.gaze.pupil_left_coords()  # 왼쪽 눈동자의 위치
        right_pupil = self.gaze.pupil_right_coords()  # 오른쪽 눈동자의 위치

        if left_pupil and right_pupil:
            left_data = (str(left_pupil).split(','))
            left_x_data = (left_data[0].split('('))[1]
            left_y_data = (left_data[1].split(')'))[0]

            right_data = (str(right_pupil).split(','))
            right_x_data = (right_data[0].split('('))[1]
            right_y_data = (right_data[1].split(')'))[0]

            avg_x_data = (int(left_x_data) + int(right_x_data)) / 2
            avg_y_data = (int(left_y_data) + int(right_y_data)) / 2

            self.x_data.append(1 - self.gaze.horizontal_ratio())
            self.y_data.append(1 - self.gaze.vertical_ratio())
            print(1 - self.gaze.horizontal_ratio(), 1 - self.gaze.vertical_ratio())
