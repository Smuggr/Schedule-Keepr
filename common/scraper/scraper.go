// scraper.go
package scraper

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"smuggr.xyz/schedule-keepr/common/config"
	"smuggr.xyz/schedule-keepr/common/utils"

	"github.com/PuerkitoBio/goquery"
)

var Config config.ScraperConfig

type TimeString string

// ToTimestamp converts a TimeString to a Timestamp struct.
func (t TimeString) ToTimestamp() (Timestamp, error) {
	parts := strings.Split(string(t), ":")
	if len(parts) < 2 || len(parts) > 3 {
		return Timestamp{}, fmt.Errorf("invalid time format: %s", t)
	}

	hour, err := strconv.Atoi(parts[0])
	if err != nil {
		return Timestamp{}, fmt.Errorf("invalid hour: %w", err)
	}

	minute, err := strconv.Atoi(parts[1])
	if err != nil {
		return Timestamp{}, fmt.Errorf("invalid minute: %w", err)
	}

	second := 0
	if len(parts) == 3 {
		second, err = strconv.Atoi(parts[2])
		if err != nil {
			return Timestamp{}, fmt.Errorf("invalid second: %w", err)
		}
	}

	return Timestamp{Hour: hour, Minute: minute, Second: second}, nil
}

type Timestamp struct {
	Hour   int
	Minute int
	Second int
}

func (t Timestamp) String() string {
	return fmt.Sprintf("%02d:%02d:%02d", t.Hour, t.Minute, t.Second)
}

// Scrapes the page and returns the time strings for that schedule
func scrapeSchedule(url string) []TimeString {
	resp, err := http.Get(url)
	if err != nil {
		return nil
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return nil
	}

	var timestamps []TimeString

	// Find all <td> elements with class 'g'
	doc.Find("td.g").Each(func(index int, item *goquery.Selection) {
		timeRange := strings.TrimSpace(item.Text())

		times := strings.Split(timeRange, "-")
		if len(times) == 2 {
			start := TimeString(strings.TrimSpace(times[0]))
			end := TimeString(strings.TrimSpace(times[1]))

			timestamps = append(timestamps, start, end)
		}
	})

	return timestamps
}

func Initialize() error {
	Config = config.Global.Scraper
	return nil
}

// Scrapes all time strings from all schedules and returns the longest ones as a slice of timestamps
func ScrapeAllTimestamps() []Timestamp {
	counter := 0
	retries := 3

	var allTimeStrings [][]TimeString

	for {
		url := fmt.Sprintf(Config.OptivumBaseUrl, counter)
		if !utils.CheckURL(url) {
			fmt.Println("failed to scrape", url, "- skipping...")
			if retries <= 0 {
				break
			}
			retries--
			counter++
			continue
		}

		timeStrings := scrapeSchedule(url)
		allTimeStrings = append(allTimeStrings, timeStrings)
		counter++

		fmt.Println("scraped", url)
	}

	var longestTimeStrings []TimeString
	for _, timeStrings := range allTimeStrings {
		if len(timeStrings) > len(longestTimeStrings) {
			longestTimeStrings = timeStrings
		}
	}

	var longestTimestamps []Timestamp
	for _, timeString := range longestTimeStrings {
		timestamp, err := timeString.ToTimestamp()
		if err != nil {
			fmt.Println("failed to convert time string to timestamp:", err)
			continue
		}
		longestTimestamps = append(longestTimestamps, timestamp)
	}

	return longestTimestamps
}
