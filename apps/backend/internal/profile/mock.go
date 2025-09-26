package profile

import (
	"log"
)

type MockProfileService struct{
	profile string
}

func NewMockService() ProfileService {
	return &MockProfileService{
		profile: "Mock Profile\n============\n\n",
	}
}

func (m *MockProfileService) Get() (string, error) {
	log.Printf("MockProfileService: Getting profile")
	return m.profile, nil
}

func (m *MockProfileService) ProcessInput(input string) error {
	log.Printf("MockProfileService: Processing input: %s", input)
	m.profile += "• " + input + "\n"
	return nil
}