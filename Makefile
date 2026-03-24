CC = gcc
CFLAGS = -Wall -Wextra -Werror -std=c11 -pedantic -g
LDFLAGS = -lm

SRC_DIR = src
BIN_DIR = bin
OUTPUT_DIR = output

TARGET = $(BIN_DIR)/tp2

SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(patsubst $(SRC_DIR)/%.c,$(BIN_DIR)/%.o,$(SRCS))

LEADER ?= 0
ETA ?= 0.0

.PHONY: all run rebuild clean dirs

all: dirs $(TARGET)

dirs:
	mkdir -p $(BIN_DIR)
	mkdir -p $(OUTPUT_DIR)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET) $(LDFLAGS)

$(BIN_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

run: all
	./$(TARGET) $(LEADER) $(ETA)

rebuild: clean all
	./$(TARGET) $(LEADER) $(ETA)

clean:
	rm -rf $(BIN_DIR)