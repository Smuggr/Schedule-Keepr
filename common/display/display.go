// display.go
package display

import (
	// "fmt"
	// "time"

	"smuggr.xyz/schedule-keepr/core/hd44780"

	"periph.io/x/conn/v3/i2c"
	"periph.io/x/conn/v3/i2c/i2creg"
)

var lcd *hd44780.HD44780
var bus i2c.BusCloser

func Initialize() error {
	b, err := i2creg.Open("/dev/i2c-0")
	if err != nil {
		return err
	}
	bus = b

	l, err := hd44780.New(&bus, 0x27, hd44780.LCD_16x2)
	if err != nil {
		return err
	}
	lcd = l

	return nil
}

func CleanUp() {
	lcd.Shutdown()
	bus.Close()
}