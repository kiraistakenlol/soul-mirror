package server

import (
	"encoding/json"
	"log"
	"net/http"
)


type ProcessResponse struct {
	Response string `json:"response"`
	Status   string `json:"status"`
}

type ErrorResponse struct {
	Error  string `json:"error"`
	Status string `json:"status"`
}

func (s *Server) processHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		s.writeError(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	input := r.URL.Query().Get("input")

	if input == "" {
		s.writeError(w, "input is required", http.StatusBadRequest)
		return
	}

	log.Printf("Processing request: %s", input)

	response, err := s.orchestrator.ProcessInput(input)
	if err != nil {
		log.Printf("Orchestrator error: %v", err)
		s.writeError(w, "Processing failed", http.StatusInternalServerError)
		return
	}

	s.writeJSON(w, ProcessResponse{
		Response: response,
		Status:   "success",
	}, http.StatusOK)
}

func (s *Server) writeError(w http.ResponseWriter, message string, statusCode int) {
	s.writeJSON(w, ErrorResponse{
		Error:  message,
		Status: "error",
	}, statusCode)
}

func (s *Server) writeJSON(w http.ResponseWriter, data interface{}, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(data)
}

func (s *Server) profileHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		s.writeError(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	profileText, err := s.profileService.Get()
	if err != nil {
		log.Printf("Failed to get profile: %v", err)
		s.writeError(w, "Failed to retrieve profile", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(profileText))
}