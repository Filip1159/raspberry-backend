# The Raspberry Monitoring backend

Hello! Welcome to my repository containing the Raspberry Monitoring app backend. Developed since I obtained my engineering degree in 2024, I finally decided to publish it after almost two years after implementing authentication :key:. The project was intended to work as a home monitoring system, but I added some other features.

#### Current features :on:

- live camera stream
- GPIO interfacing the 16x2 LCD display
- Ngrok hosting. Website available at https://apt-dane-urgently.ngrok-free.app/

#### Features in progres :construction:

- websocket communnication from GPIO keypad to UI

- programmable alarm clock build with buzzer

#### Components used

:computer: Raspberry Pi 5 module - 8GB RAM version [[Botland]](https://botland.store/raspberry-pi-5-modules-and-kits/23905-raspberry-pi-5-8gb-5056561803326.html)

:camera: Raspberry Pi Camera HD v3 12 MPx [[Botland]](https://botland.store/raspberry-pi-cameras/22480-raspberry-pi-camera-hd-v3-wide-12mpx-original-camera-for-raspberry-pi-5056561800363.html)

:symbols: LCD display 2x16 [[Botland]](https://botland.store/alphanumeric-and-graphic-displays/224-lcd-display-2x16-blue-characters-5903351241380.html)

:1234: 4x4 membrane keypad [[Botland]](https://botland.store/keyboards-for-arduino/17119-self-adhesive-membrane-keyboard-4x4-16-keys-5903351247870.html)

A custom made 3D printed frame with tall camera stand - shared soon

#### Software

:cd: Raspberry Pi OS 12 (Bookworm)

:snake: Python + Flask. As a Java developer I keep struggling with this language, but I find it really educational

:traffic_light: `gpiozero` python library for Raspberry Pi that handles raw GPIO communication

:video_camera: [[MediaMTX]](https://github.com/bluenviron/mediamtx) server that provides live camera stream via the WebRTC protocol

:satellite: [[Ngnix]](https://nginx.org/) server configured as reverse proxy to both Python backend and MediaMTX server

:earth_africa: [[Ngrok]](https://ngrok.com/) web hosting