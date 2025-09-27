package logging

import (
	"log/slog"
	"os"
)

func InitLogger(environment string) *slog.Logger {
	var handler slog.Handler
	
	if environment == "development" {
		handler = slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
			Level: slog.LevelDebug,
		})
	} else {
		handler = slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
			Level: slog.LevelInfo,
		})
	}
	
	return slog.New(handler)
}