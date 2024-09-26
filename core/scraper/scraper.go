// scraper.go
package scraper

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/PuerkitoBio/goquery"
)

// Checks if the URL is reachable
func checkURL(url string) bool {
	resp, err := http.Get(url)
	if err != nil {
		return false
	}
	defer resp.Body.Close()

	return resp.StatusCode == http.StatusOK
}

// Scrapes the page and returns the timestamps for that class
func ScrapeTimestamps(url string) []string {
	resp, err := http.Get(url)
	if err != nil {
		return nil
	}
	defer resp.Body.Close()

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return nil
	}

	var timestamps []string

	// Find all <td> elements with class 'g'
	doc.Find("td.g").Each(func(index int, item *goquery.Selection) {
		timeRange := strings.TrimSpace(item.Text())
		
		times := strings.Split(timeRange, "-")
		if len(times) == 2 {
			start := strings.TrimSpace(times[0])
			end := strings.TrimSpace(times[1])

			timestamps = append(timestamps, start, end)
		}
	})

	return timestamps
}

// Scrapes all timestamps from all classes and returns the longest one
func ScrapeAllTimestamps() []string {
	counter := 0
	retries := 3
	baseURL := "https://zsem.edu.pl/plany/plany/o%d.html"
	var allTimestamps [][]string

	for {
		url := fmt.Sprintf(baseURL, counter)
		if !checkURL(url) {
			fmt.Println("Failed to scrape", url, "- Skipping...")
			if retries <= 0 {
				break
			}
			retries--
			counter++
			continue
		}

		timestamps := ScrapeTimestamps(url)
		allTimestamps = append(allTimestamps, timestamps)
		counter++

		fmt.Println("Scraped", url)
	}

	var longestTimestamp []string
	for _, timestamps := range allTimestamps {
		if len(timestamps) > len(longestTimestamp) {
			longestTimestamp = timestamps
		}
	}

	return longestTimestamp
}