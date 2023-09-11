import asyncio
import io
import cv2
import numpy as np
from PIL import Image
import multiprocessing

def process_a(frame_queue, coordinate, start_event):
    """
    Process and analyze the image frames to detect circles.

    Args:
    - frame_queue (multiprocessing.Queue): A queue containing image frames.
    - coordinate (multiprocessing.Array): A shared array for x and y coordinates.
    - start_event (multiprocessing.Event): Event to signal readiness of this process.
    """
    print("process_a started")
    start_event.set()  # Signal that process_a is ready
    while True:
        image = frame_queue.get()
        print("Image frame received in process_a")

        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect circles using the Hough transform
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
            # Handle situations where no circle is detected
            coordinate[0], coordinate[1] = 0, 0

async def send_coordinates(writer, coordinate):
    """
    Continuously send the detected coordinates to the server.

    Args:
    - writer (StreamWriter): Output stream for writing data.
    - coordinate (multiprocessing.Array): Shared array containing x and y coordinates.
    """
    while True:
        x, y = int(coordinate[0]), int(coordinate[1])
        data = f"{x:04},{y:04}".encode()  # Ensure x and y are always 4 characters long

        writer.write(data)
        await writer.drain()
        await asyncio.sleep(0.03)

async def echo_client(frame_queue, coordinate, start_event):
    """
    Main client routine to communicate with the server.

    Args:
    - frame_queue (multiprocessing.Queue): A queue to put image frames.
    - coordinate (multiprocessing.Array): Shared array containing x and y coordinates.
    - start_event (multiprocessing.Event): Event to check readiness of the image processing function.
    """
    reader, writer = await asyncio.open_connection('127.0.0.1', 9001)
    asyncio.create_task(send_coordinates(writer, coordinate))
    
    print("Waiting for process_a to be ready...")
    start_event.wait()
    print("Starting main loop to receive images...")

    while True:
        size_data = await reader.readexactly(4)
        size = int.from_bytes(size_data, 'big')
        image_data = await reader.readexactly(size)
        image = Image.open(io.BytesIO(image_data))
        frame_queue.put(image)
        
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        cv2.imshow("Bouncing Ball", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            frame_queue.put(None)  # signal to end process_a
            break

if __name__ == "__main__":
    # Shared variables among processes
    coordinate = multiprocessing.Array('i', [0, 0])
    frame_queue = multiprocessing.Queue()
    start_event = multiprocessing.Event()
    
    p = multiprocessing.Process(target=process_a, args=(frame_queue, coordinate, start_event))
    p.start()
    
    asyncio.run(echo_client(frame_queue, coordinate, start_event))
    p.join()
    cv2.destroyAllWindows()
