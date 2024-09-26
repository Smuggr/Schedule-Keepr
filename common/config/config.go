// config.go
package config

import (
	"fmt"
	"os"

	"github.com/joho/godotenv"
	"github.com/spf13/viper"
)

var Global GlobalConfig

func loadEnv() error {
	err := godotenv.Load()
	if err != nil {
		return err
	}

	return nil
}

func loadConfig(config *GlobalConfig) error {
	if err := viper.ReadInConfig(); err != nil {
		return err
	}

	err := viper.Unmarshal(config)
	if err != nil {
		return err
	}

	return nil
}

func Initialize() error {
	fmt.Println("Initializing config...")

	if err := loadEnv(); err != nil {
		return err
	}

	viper.AddConfigPath(os.Getenv("CONFIG_PATH"))
	viper.SetConfigType(os.Getenv("CONFIG_TYPE"))

	if err := loadConfig(&Global); err != nil {
		return err
	}

	return nil
}