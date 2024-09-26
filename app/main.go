// main.go
package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"smuggr.xyz/schedule-keepr/common/config"
	"smuggr.xyz/schedule-keepr/common/scraper"
	"smuggr.xyz/schedule-keepr/core/devices"
	"smuggr.xyz/schedule-keepr/core/scheduler"

	"periph.io/x/host/v3"
)

var Scheduler *scheduler.Scheduler
var Devices *devices.Devices

// Initializes the program. If an error occurs, the program will panic.
func main() {
	signalCh := make(chan os.Signal, 1)
	signal.Notify(signalCh, os.Interrupt, syscall.SIGTERM, syscall.SIGINT)

	if err := config.Initialize(); err != nil {
		panic(err)
	}

	if _, err := host.Init(); err != nil {
		panic(err)
	}

	Scheduler = scheduler.New()
	Devices = devices.New()

	if err := scraper.Initialize(); err != nil {
		panic(err)
	}

	if err := Devices.Initialize(Scheduler); err != nil {
		panic(err)
	}
	defer Scheduler.CleanUp()

	if err := Scheduler.Initialize(); err != nil {
		panic(err)
	}
	defer Devices.CleanUp()

	fmt.Println("Waiting for shutdown...")
	<-signalCh
	fmt.Println("Exiting program.")
}
