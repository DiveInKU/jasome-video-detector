from fastapi import BackgroundTasks, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
import uvicorn
import cv2
from emotion_detector import EmotionDetector
import asyncio

app = FastAPI()
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# 크기 변환
# camera.set(3, 1640)
# camera.set(4, 1480)

templates = Jinja2Templates(directory="templates")

showing_emotion = 'false'


# async def receive_message(websocket: WebSocket):
#     global show
#     show = await websocket.receive_text()

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/emotion')
def show_emotion(show: str):
    global showing_emotion
    showing_emotion = show
    return "ok"


@app.websocket("/emotion-cam")
async def get_stream_with_emotion(websocket: WebSocket, background_tasks: BackgroundTasks):
    # 소켓 연결 -> 카메라 읽기 시작한 후에 소켓으로 이미지를 보내준다
    await websocket.accept()

    print('emotion cam started...')
    emotion_detector = EmotionDetector()

    global showing_emotion
    showing_emotion = 'false'

    try:
        while True:
            # data = await websocket.receive_text()
            success, frame = camera.read()
            # 반전
            frame = cv2.flip(frame, 2)
            if not success:
                break
            else:
                # frame = emotion_detector.add_frame(frame)
                # 소켓에 이미지 보낸다
                if showing_emotion == 'true':
                    frame = await emotion_detector.add_frame(frame, 'true')
                else:
                    # emotion_detector.add_frame(frame)
                    asyncio.create_task(emotion_detector.add_frame(frame))
                try:
                    ret, buffer = cv2.imencode('.jpg', frame)
                except:
                    print(buffer)
                    break
                await websocket.send_bytes(buffer.tobytes())
    except WebSocketDisconnect:
        print("Client disconnected")


@app.websocket("/test-cam")
async def get_stream(websocket: WebSocket):
    # 소켓 연결 -> 카메라 읽기 시작한 후에 소켓으로 이미지를 보내준다
    await websocket.accept()
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
    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
