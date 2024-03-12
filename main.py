def update_lcd():
    toggle = False  # Initialize toggle variable
    while True:
        if toggle:
            current_time = datetime.now().strftime("%d:%m:%Y")
        else:
            current_time = datetime.now().strftime("%H:%M:%S")
        lcd_string(current_time, 0x80)

        gpio_status = subprocess.run(['gpio', 'read', str(GPIO_PIN)], capture_output=True, text=True).stdout.strip()
        if gpio_status == '1':
            lcd_string("Relay: HIGH", 0xC0)
        else:
            lcd_string("Relay: LOW", 0xC0)

        toggle = not toggle  # Toggle the display format
        time.sleep(2)  # Display for 2 seconds

        # Update GPIO value every 0.1 seconds
        for _ in range(20):
            gpio_status = subprocess.run(['gpio', 'read', str(GPIO_PIN)], capture_output=True, text=True).stdout.strip()
            if gpio_status == '1':
                lcd_string("Relay: HIGH", 0xC0)
            else:
                lcd_string("Relay: LOW", 0xC0)
            time.sleep(0.1)
