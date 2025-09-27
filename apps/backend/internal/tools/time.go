package tools

import (
	"fmt"
	"time"
)

type timeTool struct{}

func NewTimeTool() Tool {
	return &timeTool{}
}

func (t *timeTool) Name() string {
	return "time"
}

func (t *timeTool) Description() string {
	return "Returns the current date and time. Useful when user asks about time, scheduling, or needs temporal context."
}

func (t *timeTool) Execute(input string) (string, error) {
	now := time.Now()
	
	// Format time in a human-readable way
	formatted := now.Format("Monday, January 2, 2006 at 3:04 PM MST")
	
	return fmt.Sprintf("Current time: %s", formatted), nil
}