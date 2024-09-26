// main.go
package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"smuggr.xyz/schedule-keepr/common/display"
	"smuggr.xyz/schedule-keepr/core/scraper"

	"periph.io/x/host/v3"
)

func main() {
	signalCh := make(chan os.Signal, 1)
	signal.Notify(signalCh, os.Interrupt, syscall.SIGTERM, syscall.SIGINT)

	if _, err := host.Init(); err != nil {
		fmt.Println("Failed to initialize host:", err)
		return
	}

	display.Initialize()

	fmt.Println(scraper.ScrapeAllTimestamps())

	fmt.Println("Waiting for shutdown...")
	<-signalCh
	fmt.Println("Exiting program.")
}
