package tools

// Context provides execution context for tools including user profile and other contextual information
type Context struct {
	Profile string `json:"profile"`
}