import time
import smbus2
from flask import Flask, request, jsonify
from datetime import datetime
import subprocess
import threading
from flask_cors import CORS

LCD_ADDRESS = 0x27
LCD_CHR = 1
LCD_CMD = 0
LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100
GPIO_PIN = 1
E_PULSE = 0.0005
E_DELAY = 0.0005

toggle_timestamps = [
    "15:15:00",
    "15:30:00",
    "16:00:00",
    "16:30:00",
    "17:00:00",
    "17:30:00",
    "18:00:00",
    "18:30:00",
    "19:00:00",
    "19:30:00",
    "20:00:00"
]

bus = smbus2.SMBus(0)

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    bus.write_byte(LCD_ADDRESS, bits_high)
    lcd_toggle_enable(bits_high)
    bus.write_byte(LCD_ADDRESS, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    time.sleep(E_DELAY)
    bus.write_byte(LCD_ADDRESS, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(LCD_ADDRESS, (bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(16, " ")
    lcd_byte(0x80 | line, LCD_CMD)
    for i in range(16):
        lcd_byte(ord(message[i]), LCD_CHR)

def lcd_clear():
    lcd_byte(0x08, LCD_CMD)
    
    for _ in range(16):
        lcd_byte(ord(" "), LCD_CHR)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_clear()

def toggle_gpio(state):
    if state:
        subprocess.run(['gpio', 'write', str(GPIO_PIN), '1'])
    else:
        subprocess.run(['gpio', 'write', str(GPIO_PIN), '0'])

def update_lcd():
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        lcd_string(current_time, 0x80)
        gpio_status = subprocess.run(['gpio', 'read', str(GPIO_PIN)], capture_output=True, text=True).stdout.strip()
        if gpio_status == '1':
            lcd_string("HIGH " + current_date, 0xC0)
        else:
            lcd_string("LOW  " + current_date, 0xC0)

        if current_time in toggle_timestamps:
            toggle_gpio(True)
            time.sleep(5)
            toggle_gpio(False)
        
        time.sleep(0.1)

app = Flask(__name__)
CORS(app)

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
    gpio_status = subprocess.run(['gpio', 'read', str(GPIO_PIN)], capture_output=True, text=True).stdout.strip()
    return jsonify({'gpio_status': gpio_status})

if __name__ == '__main__':
    subprocess.run(['gpio', 'export', str(GPIO_PIN), 'out'])
    lcd_byte(0x80, LCD_CMD)
    lcd_init()
    time.sleep(1)
    lcd_clear()
    lcd_thread = threading.Thread(target=update_lcd)
    lcd_thread.daemon = True
    lcd_thread.start()
    app.run(host='0.0.0.0', port=5000)
