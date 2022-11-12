import websockets
import asyncio
import cv2
import numpy as np

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)


async def main():
    url = 'ws://127.0.0.1:8000/ws'

    async with websockets.connect(url) as ws:
        # count = 1
        while True:
            contents = await ws.recv()
            arr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)

            # cv2.imwrite("frame%d.jpg" % count, frame)
            # count += 1


asyncio.run(main())