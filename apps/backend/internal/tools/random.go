// randomTool generates various random values including numbers, coin flips, and dice rolls.
package tools

import (
	"fmt"
	"math/rand"
)

type randomTool struct{}

func NewRandomTool() Tool {
	return &randomTool{}
}

func (t *randomTool) Name() string {
	return "random"
}

func (t *randomTool) Description() string {
	return "Generates random numbers, useful for decision making, picking options, or games"
}

func (t *randomTool) Execute(input string, context Context) (string, error) {
	// Generate different types of random values
	randomInt := rand.Intn(100) + 1  // 1-100
	randomFloat := rand.Float64()    // 0.0-1.0
	coinFlip := "heads"
	if rand.Intn(2) == 1 {
		coinFlip = "tails"
	}
	diceRoll := rand.Intn(6) + 1  // 1-6
	
	return fmt.Sprintf("Random number (1-100): %d | Coin flip: %s | Dice roll: %d | Random decimal: %.3f", 
		randomInt, coinFlip, diceRoll, randomFloat), nil
}