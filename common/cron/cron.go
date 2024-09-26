// cron.go
package cron

import (
	//"time"

	"smuggr.xyz/schedule-keepr/common/scraper"
)

type Cron struct {
	//timer     *time.Timer
	timestamp scraper.Timestamp	
}

func New(timestamp scraper.Timestamp) *Cron {



	return &Cron{timestamp: timestamp}
}