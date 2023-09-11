import asyncio
import cv2
import numpy as np
import av
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack

import logging
logging.basicConfig(level=logging.DEBUG)

class BallTrackStream(MediaStreamTrack):
    """
    A custom MediaStreamTrack implementation that draws a bouncing ball in the video stream.
    """
    def __init__(self):
        """
        Initialize the BallTrackStream with default parameters.
        """
        super().__init__()  # initialize parent class
        self.kind = "video"
        self._direction = "sendonly"
        self.width = 640
        self.height = 480
        self.ball_radius = 20
        self.ball_speed_x = 5
        self.ball_speed_y = 3
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2

    def draw_frame(self):
        """
        Draw a frame with the ball in its current position.

        Returns:
            np.ndarray: A frame with the ball drawn on it.
        """
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
    
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        if self.ball_x + self.ball_radius >= self.width or self.ball_x - self.ball_radius <= 0:
            self.ball_speed_x *= -1
        if self.ball_y + self.ball_radius >= self.height or self.ball_y - self.ball_radius <= 0:
            self.ball_speed_y *= -1
        
        cv2.circle(frame, (self.ball_x, self.ball_y), self.ball_radius, (0, 255, 0), -1)
        return frame

    async def recv(self):
        """
        Asynchronously receive a frame and return it in AIORTC's expected format.

        Returns:
            av.VideoFrame: The video frame with the ball drawn on it.
        """
        pts, time_base = await self.next_timestamp()
        
        frame = self.draw_frame()

        # Convert the frame to aiortc's VideoFrame
        video_frame = av.VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame


async def echo_handler(reader, writer):
    """
    Asynchronous handler to set up the WebRTC connection and handle data transfer.
    """
    pc = RTCPeerConnection()
    pc.on("datachannel", lambda channel: print("Data channel created:", channel.label))

    # Track for our video stream
    local_video = BallTrackStream()
    pc.addTrack(local_video)

    # Offer
    data = await reader.read(1000)
    offer = RTCSessionDescription(sdp=data.decode("utf-8"), type="offer")
    await pc.setRemoteDescription(offer)

    # Answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Send the answer
    writer.write(str(answer).encode())
    await writer.drain()

    # Read coordinates from client
    data = await reader.read(9)
    x, y = map(int, data.decode().split(','))
    error = ((x - local_video.ball_x) ** 2 + (y - local_video.ball_y) ** 2) ** 0.5
    print(f"Received: ({x}, {y}), Actual: ({local_video.ball_x}, {local_video.ball_y}), Error: {error:.2f}")

    # Hold the connection open until the app is interrupted
    await pc.wait_closed()

    writer.close()
    await writer.wait_closed()


async def echo_server():
    """
    Start an echo server that awaits connections on localhost and port 9001.
    """
    server = await asyncio.start_server(echo_handler, '127.0.0.1', 9001)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    """
    Main execution point. Starts the echo server.
    """
    asyncio.run(echo_server())
