from fastapi import BackgroundTasks, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
from websockets.exceptions import ConnectionClosedError
from gaze_tracking.gaze_tracker import GazeTracker
from emotion_detector import EmotionDetector
import asyncio
from datetime import datetime
from io import BytesIO
from fastapi import Response, HTTPException, status
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import os
import matplotlib.pyplot as plt

os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'

app = FastAPI()

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 크기 변환
# camera.set(3, 1640)
# camera.set(4, 1480)

templates = Jinja2Templates(directory="templates")

showing_emotion = 'false'

emotion_detector = EmotionDetector()
gaze_tracker = GazeTracker()
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised", "neutral"]


# async def receive_message(websocket: WebSocket):
#     global show
#     show = await websocket.receive_text()

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 감정 분석 결과 화면에 보여준다
@app.get('/emotion')
async def show_emotion(show: str):
    global showing_emotion
    showing_emotion = show


# 면접 시작한다 (감정 초기화)
@app.get('/start-interview')
async def start_analysis():
    emotion_detector.start_emotion_analysis()


class EmotionList(BaseModel):
    emotions: list[str] = []
    values:  list[float] = []
    x_data:  list[float] = []
    y_data:  list[float] = []



@app.get('/stop-interview', response_model=EmotionList)
async def show_result():
    emotion_detector.end_emotion_analysis()
    # try:
    #     plt, happy_per = emotion_detector.get_happy_result()
    # except ZeroDivisionError:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # return str(happy_per)
    print(gaze_tracker.x_data, gaze_tracker.y_data)
    plt.scatter(gaze_tracker.x_data, gaze_tracker.y_data, c='red', alpha=0.5, s=100)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.savefig('save.png')
    # x_data: 오른쪽 -> 왼쪽
    # y_data: 위 -> 아래
    print({'emotions': EMOTIONS, 'values': emotion_detector.emotion_cal, 'x_data': gaze_tracker.x_data, 'y_data': gaze_tracker.y_data})
    return {'emotions': EMOTIONS, 'values': emotion_detector.emotion_cal, 'x_data': gaze_tracker.x_data, 'y_data': gaze_tracker.y_data}


@app.websocket("/emotion-cam")
async def get_stream_with_emotion(websocket: WebSocket, background_tasks: BackgroundTasks):
    # 소켓 연결 -> 카메라 읽기 시작한 후에 소켓으로 이미지를 보내준다
    await websocket.accept()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    print('emotion cam started...')
    # emotion_detector.start_emotion_analysis()

    global showing_emotion
    showing_emotion = 'false'

    try:
        while True:
            # data = await websocket.receive_text()
            success, frame = camera.read()
            # 반전
            frame = cv2.flip(frame, 2)
            if not success:
                print('fail...')
                break
            else:
                # frame = emotion_detector.add_frame(frame)
                # 소켓에 이미지 보낸다
                # if emotion_detector.detecting:
                # frame = await emotion_detector.add_frame(frame, 'true')
                if showing_emotion == 'true':
                    frame = await emotion_detector.add_frame(frame, 'true')
                else:
                    # emotion_detector.add_frame(frame)
                    asyncio.create_task(emotion_detector.add_frame(frame))
                asyncio.create_task(gaze_tracker.add_frame(frame))
                ret, buffer = cv2.imencode('.jpg', frame)
                await websocket.send_bytes(buffer.tobytes())
    except ConnectionClosedError:
        print("Client disconnected")
    camera.release()


@app.websocket("/test-cam")
async def get_stream(websocket: WebSocket):
    # 소켓 연결 -> 카메라 읽기 시작한 후에 소켓으로 이미지를 보내준다
    await websocket.accept()

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    print('test cam started...')
    try:
        while True:
            success, frame = camera.read()
            # 반전
            frame = cv2.flip(frame, 2)
            if not success:
                break
            else:
                try:
                    ret, buffer = cv2.imencode('.jpg', frame)
                except:
                    print(buffer)
                    break
                await websocket.send_bytes(buffer.tobytes())
    except ConnectionClosedError:
        print("Client disconnected")
    camera.release()


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
