import asyncio
import cv2
import numpy as np
import multiprocessing as mp
import av
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription

import logging

logging.basicConfig(level=logging.DEBUG)


def ball_detect_process(frame_queue, coordinate):
    """
    Continuously process frames to detect a ball and update its coordinates.

    Args:
    - frame_queue (mp.Queue): Queue from which frames are received for processing.
    - coordinate (mp.Array): Shared array where detected ball coordinates are stored.
    """
    while True:
        image = frame_queue.get()
        if image is None:
            break
        
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT, dp=1.2,
            minDist=30, param1=50,
            param2=30, minRadius=5,
            maxRadius=30
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            (x, y, r) = circles[0]
            coordinate[0], coordinate[1] = x, y
        else:
            coordinate[0], coordinate[1] = 0, 0


class RemoteVideoStream:
    """
    Handles the incoming video stream, displays the video and sends the ball's coordinates.

    Attributes:
    - track (MediaStreamTrack): Video track.
    - data_channel: WebRTC data channel to send coordinates.
    - frame_queue (mp.Queue): Queue to send frames for processing.
    - coordinate (mp.Array): Shared array where detected ball coordinates are stored.
    """
    def __init__(self, track, data_channel, frame_queue, coordinate):
        self.track = track
        self.data_channel = data_channel
        self.frame_queue = frame_queue
        self.coordinate = coordinate

    async def display(self):
        """Display the video stream and send ball coordinates through the data channel."""
        while True:
            frame = await self.track.recv()
            if isinstance(frame, av.VideoFrame):
                img = frame.to_ndarray(format="bgr24")
                self.frame_queue.put(img)

                cv2.imshow("Ball Frame", img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                x, y = int(self.coordinate[0]), int(self.coordinate[1])
                data = f"{x:04},{y:04}".encode()
                self.data_channel.send(data)


async def webrtc_client():
    """Main WebRTC client logic for connecting, sending offer and receiving video streams."""
    # Connect to the server
    reader, writer = await asyncio.open_connection('127.0.0.1', 9001)

    pc = RTCPeerConnection()
    frame_queue = mp.Queue()
    coordinate = mp.Array('i', [0, 0])

    p = mp.Process(target=ball_detect_process, args=(frame_queue, coordinate))
    p.start()

    def on_track(track):
        """Handler for incoming media streams."""
        if track.kind == "video":
            print("Receiving video track.")
            remote_stream = RemoteVideoStream(track, data_channel, frame_queue, coordinate)
            asyncio.create_task(remote_stream.display())

    pc.on("track", on_track)
    data_channel = pc.createDataChannel('chat')
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)

    offer_sdp = str(pc.localDescription.sdp)
    writer.write((f"{len(offer_sdp):04}" + offer_sdp).encode())

    # Wait for server to send back an answer
    data = await reader.read(4)
    length = int(data.decode())
    data = await reader.read(length)
    answer_sdp = data.decode()

    answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
    await pc.setRemoteDescription(answer)

    writer.close()


if __name__ == "__main__":
    asyncio.run(webrtc_client())
