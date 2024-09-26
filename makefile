PROJECT_NAME := $(notdir $(CURDIR))
BINARY_NAME := $(PROJECT_NAME)

PROJECT_ROOT := $(CURDIR)
BUILD_DIR := $(PROJECT_ROOT)/build
CURRENT_BUILD_DIR := $(BUILD_DIR)/$(BINARY_NAME)
REMOTE_HOST := schedule-keepr

.PHONY: all
all: build sync

.PHONY: build
build: | $(CURRENT_BUILD_DIR)
	@echo "Building application..."
	@GOOS=linux GOARCH=arm GOARM=7 go build -o $(CURRENT_BUILD_DIR)/$(BINARY_NAME) ./app/main.go

$(CURRENT_BUILD_DIR):
	@mkdir -p $(CURRENT_BUILD_DIR)

.PHONY: sync
sync: 
	@echo "Syncing application to client..."
	@rsync -av --delete $(CURRENT_BUILD_DIR)/ $(REMOTE_HOST):/home/pi/Schedule-Keepr

.PHONY: clean
clean:
	@echo "Cleaning up..."
	@rm -rf $(BUILD_DIR)

.PHONY: help
help:
	@echo "Usage:"
	@echo "  make                      Build, sync, and run the application on the client machine"
	@echo "  make build                Build the application"
	@echo "  make sync                 Sync application to client"
	@echo "  make clean                Clean up build files"
	@echo "  make help                 Show this help message"
