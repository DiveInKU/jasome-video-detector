import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from keras_preprocessing.image import img_to_array
import imutils
import cv2
from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt

plt.switch_backend('agg')

'''
초기화 시에 빈 배열을 생성한다.
frame을 받으면서 분석하여 업데이트한다.
함수를 통해 결과를 보내준다.
'''

# parameters for loading data and images
detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
emotion_model_path = 'models/_mini_XCEPTION.102-0.66.hdf5'

# hyper-parameters for bounding boxes shape
# loading models
face_detection = cv2.CascadeClassifier(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]
graph_label = ["smile", "non-smile"]


class EmotionDetector:
    def __init__(self):
        self.analysis_result = {}

    def is_analyzed(self, interview_number):
        emotion_all = 0
        for i in range(7):
            emotion_all += self.analysis_result[interview_number][i]
            if emotion_all != 0:
                break
        if emotion_all == 0:
            return False
        else:
            return True

    def get_result(self, interview_number):
        return self.analysis_result[interview_number]

    def get_happy_result(self, interview_number):
        emotion_all = 0
        for i in range(7):
            print(str(EMOTIONS[i]) + ":" + str(self.analysis_result[interview_number][i]))  # emotion 값 확인
            emotion_all += self.analysis_result[interview_number][i]
        happy_per = self.analysis_result[interview_number][3] / emotion_all
        print("happy percentile : " + str(happy_per * 100) + "%")
        ratio = [happy_per * 100, 100 - happy_per * 100]
        explode = [0.1, 0.1]  # 중심에서 벗어난 정도
        colors = ['gold', 'lightgray']
        plt.pie(ratio, labels=graph_label, autopct='%.1f%%', explode=explode, shadow=True, colors=colors)
        return plt, happy_per

    async def add_frame(self, frame, interview_number):
        # reading the frame
        frame = imutils.resize(frame, width=300)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                                flags=cv2.CASCADE_SCALE_IMAGE)

        canvas = np.zeros((250, 300, 3), dtype="uint8")
        frame_clone = frame.copy()
        if len(faces) > 0:
            faces = sorted(faces, reverse=True,
                           key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
            # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
            # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (64, 64))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            preds = emotion_classifier.predict(roi)[0]
            emotion_probability = np.max(preds)
            label = EMOTIONS[preds.argmax()]
            print(label)
            return label
        else:
            return frame

        # for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
        #     # construct the label text
        #     text = "{}: {:.2f}%".format(emotion, prob * 100)
        #
        #     # draw the label + probability bar on the canvas
        #     # emoji_face = feelings_faces[np.argmax(preds)]
        #
        #     w = int(prob * 300)
        #     cv2.rectangle(canvas, (7, (i * 35) + 5),
        #                   (w, (i * 35) + 35), (0, 0, 255), -1)
        #     cv2.putText(canvas, text, (10, (i * 35) + 23),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.45,
        #                 (255, 255, 255), 2)
        #     cv2.putText(frame_clone, label, (fX, fY - 10),
        #                 cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        #     cv2.rectangle(frame_clone, (fX, fY), (fX + fW, fY + fH),
        #                   (0, 0, 255), 2)
        #     self.analysis_result[client_number][preds.argmax()] = self.analysis_result[client_number][preds.argmax()] + 1
        #    for c in range(0, 3):
        #        frame[200:320, 10:130, c] = emoji_face[:, :, c] * \
        #        (emoji_face[:, :, 3] / 255.0) + frame[200:320,
        #        10:130, c] * (1.0 - emoji_face[:, :, 3] / 255.0)
        # if show_emotion == 'true':
        #     return frame_clone
        # else:
        #     return frame
