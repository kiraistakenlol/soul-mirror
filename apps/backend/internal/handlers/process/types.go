package process

type Request struct {
	Input string `json:"input" form:"input" binding:"required"`
}
