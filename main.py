import time
import smbus2
from flask import Flask, request
from datetime import datetime
import subprocess

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

app = Flask(__name__)

@app.route('/on', methods=['POST'])
def gpio_on():
	toggle_gpio(True)
	return 'GPIO ON'

@app.route('/off', methods=['POST'])
def gpio_off():
	toggle_gpio(False)
	return 'GPIO OFF'

def get_current_time():
	# Get current time in HH:MM:SS format
	return datetime.now().strftime("%H:%M:%S")

if __name__ == '__main__':
	# Setup GPIO pin
	subprocess.run(['gpio', 'export', str(GPIO_PIN), 'out'])

	# Initialize display
	lcd_init()

	app.run(host='0.0.0.0', port=5000)
	
	# Loop to continuously update time on LCD
	try:
		while True:
			current_time = get_current_time()
			lcd_string("Current Time:", 0)
			lcd_string(current_time, 1)
			time.sleep(1)  # Update time every second

	except KeyboardInterrupt:
		pass

	finally:
		lcd_clear()

