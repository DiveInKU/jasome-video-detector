"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""
import matplotlib.pyplot as plt

import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
x_data = []
y_data = []

while True:
    # We get a new frame from the webcam
    _, frame = webcam.read()

    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""

    if gaze.is_blinking():
        text = "Blinking"
    elif gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

    left_pupil = gaze.pupil_left_coords()  # 왼쪽 눈동자의 위치
    right_pupil = gaze.pupil_right_coords()  # 오른쪽 눈동자의 위치
    cv2.putText(frame, "horizontal:  " + str(gaze.horizontal_ratio()), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
    cv2.putText(frame, "vertical: " + str(gaze.vertical_ratio()), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)


    if left_pupil and right_pupil:
        left_data = (str(left_pupil).split(','))
        left_x_data = (left_data[0].split('('))[1]
        left_y_data = (left_data[1].split(')'))[0]

        right_data = (str(right_pupil).split(','))
        right_x_data = (right_data[0].split('('))[1]
        right_y_data = (right_data[1].split(')'))[0]

        avg_x_data = (int(left_x_data) + int(right_x_data)) / 2
        avg_y_data = (int(left_y_data) + int(right_y_data)) / 2

        # print(avg_x_data, avg_y_data)
        x_data.append(gaze.horizontal_ratio())
        y_data.append(gaze.vertical_ratio())

    # print("Left pupil:  "+ str(left_pupil))
    # print("Right pupil:  "+ str(right_pupil))

    cv2.imshow("Demo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

plt.scatter(x_data, y_data, c='red', alpha=0.5, s=100)
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.show()
webcam.release()
cv2.destroyAllWindows()
