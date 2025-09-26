package profile

import (
	"fmt"
	"log"
	"sync"
)

type ProfileService interface {
	Get() (string, error)
	ProcessInput(input string) error
}

type service struct {
	profile string
	mutex   sync.RWMutex
}

func NewService() ProfileService {
	return &service{
		profile: "User Profile\n===========\n\n",
	}
}

func (s *service) Get() (string, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	log.Printf("ProfileService: Retrieved profile")
	return s.profile, nil
}

func (s *service) ProcessInput(input string) error {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	log.Printf("ProfileService: Processing input: %s", input)

	// Simply append input to profile with timestamp-like marker
	s.profile += fmt.Sprintf("• %s\n", input)

	log.Printf("ProfileService: Added input to profile")
	return nil
}