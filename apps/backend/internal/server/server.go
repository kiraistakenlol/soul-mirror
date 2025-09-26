package server

import (
	"fmt"
	"log"
	"net/http"

	"github.com/kirillsobolev/soul-mirror/backend/internal/orchestrator"
	"github.com/kirillsobolev/soul-mirror/backend/internal/profile"
)

type Server struct {
	orchestrator   orchestrator.Orchestrator
	profileService profile.ProfileService
	port           string
}

func New(orch orchestrator.Orchestrator, profileService profile.ProfileService, port string) *Server {
	return &Server{
		orchestrator:   orch,
		profileService: profileService,
		port:           port,
	}
}

func (s *Server) Start() error {
	http.HandleFunc("/health", s.healthHandler)
	http.HandleFunc("/process", s.processHandler)
	http.HandleFunc("/profile", s.profileHandler)

	log.Printf("Server starting on :%s", s.port)
	return http.ListenAndServe(fmt.Sprintf(":%s", s.port), nil)
}

func (s *Server) healthHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}