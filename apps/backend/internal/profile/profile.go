// profile manages and stores user profile data accumulated from inputs.
package profile

import (
	"log"
	"sync"

	"github.com/kirillsobolev/soul-mirror/backend/internal/llm"
)

type ProfileUpdateResponse struct {
	UpdatedProfile   string
	ExtractedTargets []llm.ExtractionResult
}

type ProfileService interface {
	Get() (string, error)
	ProcessInput(input string) (*ProfileUpdateResponse, error)
}

type service struct {
	profile           string
	extractionTargets []llm.ExtractionTarget
	llmService        llm.LLMService
	mutex             sync.RWMutex
}

func NewService(llmService llm.LLMService) ProfileService {
	return &service{
		profile:    "",
		llmService: llmService,
		extractionTargets: []llm.ExtractionTarget{
			{
				Name:        "personal_info",
				Description: "Basic personal information including name, age, location, gender, nationality, occupation, family status, and other demographic details",
			},
			{
				Name:        "interests",
				Description: "Hobbies, interests, activities the person enjoys, favorite things, entertainment preferences, sports, creative pursuits, and leisure activities",
			},
			{
				Name:        "goals",
				Description: "Goals, aspirations, ambitions, things the person wants to achieve, improve, learn, or accomplish in life, career, or personal development",
			},
			{
				Name:        "personality",
				Description: "Personality traits, behavioral patterns, communication style, values, beliefs, character qualities, emotional tendencies, and psychological characteristics",
			},
		},
	}
}

func (s *service) Get() (string, error) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()

	log.Printf("ProfileService: Retrieved profile")
	return s.profile, nil
}

func (s *service) ProcessInput(input string) (*ProfileUpdateResponse, error) {
	s.mutex.Lock()
	defer s.mutex.Unlock()

	log.Printf("ProfileService: Processing input: %s", input)

	response, err := s.llmService.UpdateProfile(input, s.profile, s.extractionTargets)
	if err != nil {
		log.Printf("ProfileService: LLM extraction failed: %v", err)
		return &ProfileUpdateResponse{
			UpdatedProfile:   s.profile,
			ExtractedTargets: []llm.ExtractionResult{},
		}, err
	}

	s.profile = response.UpdatedProfile
	log.Printf("ProfileService: Successfully updated profile with %d extractions", len(response.ExtractedTargets))

	return &ProfileUpdateResponse{
		UpdatedProfile:   response.UpdatedProfile,
		ExtractedTargets: response.ExtractedTargets,
	}, nil
}
