import asyncio

from flask import Flask, render_template
from flask_socketio import SocketIO
from fastapi import FastAPI, Request
from fastapi_socketio import SocketManager
from time import sleep
import cv2
import json
import base64
from flask_cors import CORS
import numpy as np
import json
from emotion_detector2 import EmotionDetector

# cap=cv2.VideoCapture(0)  ##when removing debug=True or using gevent or eventlet uncomment this line and comment the cap=cv2.VideoCapture(0) in gen(json)
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='http://localhost:3000')

interview_number = 0

emotion_detector = EmotionDetector()
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]


@app.route('/')
def index():
    return render_template('index2.html')


# @socketio.on('button')
# async def receive_message(msg):
#     print(msg)
@socketio.on('interview_start')
def client_in():
    global interview_number
    interview_number += 1
    socketio.emit('interview_number', interview_number)


@socketio.on('check')
def gen(json):
    cap = cv2.VideoCapture(0)
    while (cap.isOpened()):
        ret, img = cap.read()
        if ret:
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            frame = base64.encodebytes(frame).decode("utf-8")
            message(frame)
            socketio.sleep(0)
        else:
            break


@socketio.on('image')
def receiveImage(request):
    current_interview = request['interviewNumber']
    base64_image_url = request['image']
    # print(base64_image_url)
    # ret, buffer = cv2.imencode('.webp', img)
    header, data = base64_image_url.split(',', 1)
    image_data = base64.b64decode(data)
    np_array = np.frombuffer(image_data, np.uint8)
    # asyncio.create_task(emotion_detector.add_frame(np_array, current_interview))
    result = emotion_detector.add_frame(np_array, current_interview)


@socketio.on('query_result')
def getResult(request):
    current_interview = request['interviewNumber']
    result = {'emotions': EMOTIONS, 'values': emotion_detector.get_result(current_interview)}
    socketio.emit('result', result)


def message(json, methods=['GET', 'POST']):
    # print("Recieved message")
    socketio.emit('image', json)


if __name__ == "__main__":
    socketio.run(app, debug=True, host='127.0.0.1', port=8000)
