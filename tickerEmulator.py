import threading
import socket
import logging
import pygame
import time
import argparse
import copy

"""
    Basic UDP Pixelflut emulator by Melan 
    to help aiding in writing client software for the led ticker at nurdspace, 
    when too lazy to actually go to the space.
    
    Uses the protocol as described in 
    https://github.com/JanKlopper/pixelvloed/blob/master/protocol.md
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

class tickerEmulator():
    log = logging.getLogger("MAIN")
    pixel_buffer = {}

    def __init__(self, args):
        self.args = args
        self.display = pygame.display.set_mode((self.args.height, self.args.width))
        self.log.info(f"Starting Ticker Emulator ({self.args.height}, {self.args.width})")
        pygame.display.set_caption('Ticker Emulator')

    def pygame_loop(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

            # We need to make a copy because we can't change a dictionary
            # while we are iterating over it.
            # Also need to make a deepcopy because otherwise it's just a pointer
            pixel_buffer = copy.deepcopy(self.pixel_buffer)

            # TODO make this better and actually have it fade like the ticker at Nurdspace does
            for pixel_time in pixel_buffer:
                if (time.time() - pixel_time) >= self.args.fade:
                    self.log.info(f"Clearing pixels made at {pixel_time}")
                    for pixel in self.pixel_buffer[pixel_time]:
                        self.display.set_at((pixel[0], pixel[1]), (0, 0, 0))
                    self.pixel_buffer.pop(pixel_time)

            pygame.display.update()
            clock.tick(self.args.fps)

    def start_server(self):
        t = threading.Thread(target=self.server_thread)
        t.daemon = True
        t.start()

    def server_thread(self):
        self.log.info(f"Server running at {self.args.bind} {self.args.port}")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.args.bind, self.args.port))

        while True:
            buffer, conn = s.recvfrom(self.args.buffer)
            self.log.info(f"Received data from from {conn[0]} ({len(buffer)} bytes)")

            if buffer:
                inc = 7

                # Just like nurdspace.c we takes steps of 8 when there is an alpha channel.
                # Otherwise just increment by 7 steps for x,y and r, g, b
                if bool(buffer[1]):
                    inc = 8

                # Clear the screen before writing new pixels
                self.display.fill((0, 0, 0))

                # Store a copy of the pixels based on the time the transaction started
                pixel_time = time.time()
                self.pixel_buffer.update({pixel_time: []})

                # Also just like nurdspace.c we currently don't support the alpha channe and will just ignore it.
                for i in range(2, len(buffer), inc):
                    x = (buffer[i + 1] << 8) | buffer[i + 0]
                    y = (buffer[i + 3] << 8) | buffer[i + 2]
                    r = buffer[i + 4]
                    g = buffer[i + 5]
                    b = buffer[i + 6]
                    self.display.set_at((x, y), (r, g, b))
                    self.pixel_buffer[pixel_time].append((x, y, r, g, b))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", "-b", help="IP address to bind to.", default="0.0.0.0")
    parser.add_argument("--port", "-p", help="Port to use", default=5004)
    parser.add_argument("--buffer", help="Buffer size", default=65536)
    parser.add_argument("--fps", help="FPS", default=60)
    parser.add_argument("--fade", help="Time in seconds to wait before clearing the pixels", default=8)
    parser.add_argument("--height", help="The height of the display", default=128)
    parser.add_argument("--width", help="The width of the display", default=32)


    emu = tickerEmulator(args=parser.parse_args())
    emu.start_server()
    emu.pygame_loop()

