# Ticker Emulator

Basic UDP Pixelflut emulator, to help aiding in writing client software for the led ticker at nurdspace when too lazy to actually go to the space. Uses Pygame to render the pixels, should be platform independent!

Uses the protocol as described in 
[https://github.com/JanKlopper/pixelvloed/blob/master/protocol.md](https://github.com/JanKlopper/pixelvloed/blob/master/protocol.md)

##### command line arguments

| args     | info                                     |
|----------|------------------------------------------|
| --bind   | The IP to bind to, defaults to 0.0.0.0   |
| --port   | The port to use, defaults to 5004        |
| --buffer | Sets the buffer size, defaults to 65536  |
| --fps    | Set the pygame refresh rate, defaults to 60 FPS |
| --fade   | Seconds it takes before deleting the pixels, doesn't actually fade yet |
| --height | The height of the screen, defaults to 128 |
| --width  | The width of the screen, defaults to 32  |



