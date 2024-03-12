import time
import smbus2
from flask import Flask, request
import subprocess
import socket

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

def get_gpio_state():
    result = subprocess.run(['gpio', 'read', str(GPIO_PIN)], capture_output=True, text=True)
    return result.stdout.strip()  # Remove leading/trailing whitespace

app = Flask(__name__)

@app.route('/on', methods=['POST'])
def gpio_on():
    toggle_gpio(True)
    return 'GPIO ON'

@app.route('/off', methods=['POST'])
def gpio_off():
    toggle_gpio(False)
    return 'GPIO OFF'

@app.route('/ip')
def get_ip():
    ip_address = socket.gethostbyname(socket.gethostname())
    return ip_address

@app.route('/gpio_state')
def gpio_state():
    return get_gpio_state()

if __name__ == '__main__':
    # Setup GPIO pin
    subprocess.run(['gpio', 'export', str(GPIO_PIN), 'out'])

    # Initialize display
    lcd_init()

    # Print IP address and GPIO state to the LCD
    lcd_string("IP Address:", 0)
    lcd_string(get_ip(), 1)
    lcd_string("GPIO State:", 2)
    lcd_string(get_gpio_state(), 3)

    app.run(host='0.0.0.0', port=5000)