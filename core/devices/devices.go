// devices.go
package devices

import (
	"fmt"
	"time"

	"smuggr.xyz/schedule-keepr/common/config"
	"smuggr.xyz/schedule-keepr/common/lcd"
	"smuggr.xyz/schedule-keepr/core/scheduler"

	"periph.io/x/conn/v3/i2c"
	"periph.io/x/conn/v3/i2c/i2creg"
)

var Config config.DevicesConfig

type Devices struct {
	scheduler *scheduler.Scheduler
	display   *lcd.HD44780
	bus       i2c.BusCloser
	ticker    *time.Ticker
}

func New() *Devices {
	return &Devices{}
}

func (d *Devices) runTicker() {

}

func (d *Devices) Initialize(scheduler *scheduler.Scheduler) error {
	fmt.Println("Initializing devices...")
	
	Config = config.Global.Devices

	b, err := i2creg.Open("/dev/i2c-0")
	if err != nil {
		return err
	}
	d.bus = b
	d.scheduler = scheduler

	display, err := lcd.New(&d.bus, Config.DisplayAddress, lcd.LCD_16x2)
	if err != nil {
		return err
	}
	d.display = display

	d.display.DisplayOn()
	d.display.Clear()
	d.display.BacklightOn()
	
	d.display.ShowMessage("Initializing...", 1)

	d.ticker = time.NewTicker(1 * time.Second)
	go d.runTicker()

	return nil
}

func (d *Devices) CleanUp() {
	fmt.Println("Cleaning up devices...")
	d.display.Shutdown()
	d.bus.Close()
}