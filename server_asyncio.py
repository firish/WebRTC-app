import asyncio
from PIL import Image, ImageDraw

# Parameters for creating the ball
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 25
SPEED = 2.5

class Ball:
    """
    Represents a bouncing ball inside a defined frame.

    Attributes:
    - x (int): Current x-coordinate of the ball's center.
    - y (int): Current y-coordinate of the ball's center.
    - vx (float): Speed of the ball along the x-axis.
    - vy (float): Speed of the ball along the y-axis.
    """

    def __init__(self):
        """Initialize the ball with its starting position and speed."""
        self.x = WIDTH // 4
        self.y = HEIGHT // 4
        self.vx = SPEED
        self.vy = 2*SPEED

    def move(self):
        """Move the ball by updating its x and y coordinates."""
        self.x += self.vx
        self.y += self.vy
        # Handle bouncing off the walls
        if self.x - BALL_RADIUS < 0 or self.x + BALL_RADIUS > WIDTH:
            self.vx = -self.vx
        if self.y - BALL_RADIUS < 0 or self.y + BALL_RADIUS > HEIGHT:
            self.vy = -self.vy

    def draw(self, draw):
        """
        Draw the ball on a given image.
        
        Args:
        - draw (ImageDraw.Draw): Drawing context.
        """
        draw.ellipse((self.x - BALL_RADIUS, self.y - BALL_RADIUS, self.x + BALL_RADIUS, self.y + BALL_RADIUS), fill="red")


ball = Ball()

def create_ball_image():
    """Create and return an image with the ball drawn on it."""
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    ball.draw(draw)
    ball.move()
    return img

async def echo_handler(reader, writer):
    """
    Handle communication with the client.
    
    Args:
    - reader (StreamReader): Input stream for reading data.
    - writer (StreamWriter): Output stream for writing data.
    """
    global ball
    while True:
        data = await reader.readexactly(9)
        x, y = map(int, data.decode().split(','))
        error = ((x - ball.x)**2 + (y - ball.y)**2)**0.5
        print(f"Received: ({x}, {y}), Actual: ({ball.x}, {ball.y}), Error: {error:.2f}")
        image = create_ball_image()
        image_bytes = image.tobytes("jpeg", "RGB")
        size_data = len(image_bytes).to_bytes(4, 'big')
        writer.write(size_data + image_bytes)
        await writer.drain()
        await asyncio.sleep(0.06)  # Frame delay for 60 FPS

async def echo_server():
    """Start the server and handle incoming client connections."""
    server = await asyncio.start_server(echo_handler, '127.0.0.1', 9001)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(echo_server())
