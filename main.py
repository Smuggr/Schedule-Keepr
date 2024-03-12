import time
import smbus2
from flask import Flask, request, jsonify
from datetime import datetime
import subprocess
import threading
from flask_cors import CORS

# Define I2C address of the LCD
LCD_ADDRESS = 0x27  # Change this to your actual I2C address

# Define commands
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_BACKLIGHT = 0x08  # On

ENABLE = 0b00000100  # Enable bit

# GPIO pin for controlling
GPIO_PIN = 1  # Change this to the desired GPIO pin number

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open I2C bus
bus = smbus2.SMBus(0)  # 1 indicates /dev/i2c-1

def lcd_byte(bits, mode):
    # Send byte to data pins
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(LCD_ADDRESS, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(LCD_ADDRESS, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(LCD_ADDRESS, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(LCD_ADDRESS, (bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_string(message, line):
    # Send string to display
    message = message.ljust(16, " ")
    lcd_byte(0x80 | line, LCD_CMD)  # Move cursor to specified line
    for i in range(16):
        lcd_byte(ord(message[i]), LCD_CHR)

def lcd_clear():
    # Clear display
    lcd_byte(0x01, LCD_CMD)

def lcd_init():
    # Initialize display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_clear()

def toggle_gpio(state):
    if state:
        subprocess.run(['gpio', 'write', str(GPIO_PIN), '1'])
    else:
        subprocess.run(['gpio', 'write', str(GPIO_PIN), '0'])

def update_lcd():
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        lcd_string("Time:" + current_time, 0x80)

        gpio_status = subprocess.run(['gpio', 'read', str(GPIO_PIN)], capture_output=True, text=True).stdout.strip()
        if gpio_status == '1':
            lcd_string("Relay: HIGH", 0xC0)
        else:
            lcd_string("Relay: LOW", 0xC0)
            
        time.sleep(0.1)

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

@app.route('/on', methods=['POST'])
def gpio_on():
    toggle_gpio(True)
    return 'GPIO ON'

@app.route('/off', methods=['POST'])
def gpio_off():
    toggle_gpio(False)
    return 'GPIO OFF'

@app.route('/time', methods=['GET'])
def get_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    return jsonify({'current_time': current_time})

@app.route('/gpio_status', methods=['GET'])
def get_gpio_status():
    # Read GPIO status here and return
    # For now, let's just return a dummy value
    return jsonify({'gpio_status': 'HIGH'})

if __name__ == '__main__':
    # Setup GPIO pin
    subprocess.run(['gpio', 'export', str(GPIO_PIN), 'out'])

    # Initialize display
    lcd_init()

    # Start LCD update thread
    lcd_thread = threading.Thread(target=update_lcd)
    lcd_thread.daemon = True
    lcd_thread.start()

    app.run(host='0.0.0.0', port=5000)
