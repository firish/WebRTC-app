import pytest
import asyncio
from unittest.mock import Mock, patch
from server_asyncio import BallTrackStream, echo_handler

@pytest.mark.asyncio
async def test_ball_track_stream_recv():
    stream = BallTrackStream()
    frame = await stream.recv()
    
    # Check the dimensions and type of the frame
    assert frame.width == 640
    assert frame.height == 480
    assert frame.format.name == 'bgr24'

@pytest.mark.asyncio
async def test_echo_handler():
    # Mocks
    reader = Mock()
    writer = Mock()
    reader.read.side_effect = [
        asyncio.Future().set_result("offer_sdp".encode()), # for offer sdp
        asyncio.Future().set_result("x,y".encode())        # for coordinates
    ]
    
    # Mock aiortc's RTCPeerConnection
    with patch("your_server_module.RTCPeerConnection") as mock_pc:
        instance = mock_pc.return_value
        instance.createAnswer.return_value = "answer_sdp"
        
        await echo_handler(reader, writer)
        
        writer.write.assert_called()  # Check if the writer.write method was called

@pytest.mark.asyncio
async def test_echo_server():
    # Mock server
    mock_server = Mock()
    mock_server.serve_forever.return_value = asyncio.Future().set_result(None)
    
    with patch('asyncio.start_server', return_value=mock_server):
        await echo_server()

