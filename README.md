# Raspberry Pi Pico Button

This project aims to create a button box/macro pad that is highly customizable. Currently the button box itself acts as an input listener, transmitting all the necessary information to the host software. As such, the functionality can be easily expanded by writing more modules in the `modules` folder and defining them in the `modules.json` file.

The software that runs on the RPi Pico is in the `pico-software` folder. Everything is written in CircuitPython.

The CAD design is hosted on Onshape and can be seen [here](https://cad.onshape.com/documents/05f1e063c28af7aa2b008461/w/7f021347667894c701b17d55/e/c6a0fee94325b67b7ae888c9). The device uses a Waveshare 13992 128x128px OLED screen as a display and the rotary encoder is an EC12 24 impulse 15mm rotary encoder.

The main startup file for the host software is `main.py`. Currently only Linux is supported, Windows functionality is untested.
