// config/models.go
package config

type ScraperConfig struct {
	OptivumBaseUrl string `mapstructure:"optivum_base_url"`
}

type DevicesConfig struct {
	DisplayAddress uint16 `mapstructure:"display_address"`
	RTCAddress     uint16 `mapstructure:"rtc_address"`
}


type GlobalConfig struct {
	Scraper ScraperConfig `mapstructure:"scraper"`
	Devices DevicesConfig `mapstructure:"devices"`
}