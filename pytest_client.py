import pytest
import cv2
import asyncio
from unittest.mock import Mock, patch, MagicMock
import io
from PIL import Image, ImageDraw
from client_asyncio import process_a, send_coordinates, echo_client

@pytest.fixture
def setup_queue():
    # Create a mock for the multiprocessing queue
    queue = Mock()
    return queue

@pytest.fixture
def setup_coordinate():
    # Mock shared array
    coordinate = MagicMock()
    coordinate[0] = 0
    coordinate[1] = 0
    return coordinate

@pytest.fixture
def setup_event():
    # Mock event for process start signal
    event = Mock()
    return event


def test_process_a_circle_detection(setup_queue, setup_coordinate, setup_event):
    # Use an example image with a circle for testing
    im = Image.new("RGB", (100, 100), "white")
    d = ImageDraw.Draw(im)
    d.ellipse((25, 25, 75, 75), fill="black")
    setup_queue.get.return_value = im

    process_a(setup_queue, setup_coordinate, setup_event)
    
    assert setup_coordinate[0] != 0
    assert setup_coordinate[1] != 0

def test_send_coordinates():
    writer_mock = MagicMock()
    coordinate = [25, 50]
    
    asyncio.run(send_coordinates(writer_mock, coordinate))
    writer_mock.write.assert_called_once_with(b"0025,0050")

@patch('asyncio.open_connection')
@patch('cv2.imshow')
@patch('cv2.waitKey', return_value=0xFF ^ ord('q'))
def test_echo_client(mock_open_connection, mock_imshow, mock_waitKey, setup_queue, setup_coordinate, setup_event):
    mock_reader = MagicMock()
    mock_writer = MagicMock()
    
    size = 100
    # Create a dummy image for the server to "send"
    image = Image.new("RGB", (50, 50), "blue")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    image_data = buffer.getvalue()
    
    mock_reader.readexactly.side_effect = [
        size.to_bytes(4, 'big'), # Image size
        image_data               # Image data
    ]

    mock_open_connection.return_value = (mock_reader, mock_writer)

    asyncio.run(echo_client(setup_queue, setup_coordinate, setup_event))
    mock_imshow.assert_called_once()
