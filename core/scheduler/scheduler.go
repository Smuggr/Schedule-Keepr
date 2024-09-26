// scheduler.go
package scheduler

import (
	"fmt"

	"smuggr.xyz/schedule-keepr/common/scraper"
)

type Scheduler struct {
	Timestamps []scraper.Timestamp
}

func New() *Scheduler {
	return &Scheduler{}
}

func (s *Scheduler) Initialize() error {
	fmt.Println("Initializing scheduler...")

	s.Timestamps = scraper.ScrapeAllTimestamps()

	return nil
}

func (s *Scheduler) CleanUp() {
	fmt.Println("Cleaning up scheduler...")
}
