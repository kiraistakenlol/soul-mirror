# Agent-Cycle Architecture

## Core Concept
Transform orchestrator from single-pass command→response to a cyclic agent that can "work" over time.

## MVP: Note Management System
Strip down to orchestrator + essential tools, starting with "noteTaker" tool.

**Flow**: input → orchestrator normalizes → decides add/remove note → executes

## Key Architecture Changes

### 1. Tool Method System
**Current**: Tools have generic `Execute(input, context)` method
**New**: Tools expose multiple **Methods** with:
- Method name + description  
- Input/output specifications
- Clear signatures for LLM to understand

### 2. Orchestrator Evolution
**Current**: `ProcessInput()` → single response
**New**: Cyclic operation that can:
- Normalize user input into structured data
- Decide which tool methods to call with what arguments
- Execute multiple work cycles
- Maintain state between cycles

### 3. LLM Integration Enhancement
- LLM needs method specifications to choose tools
- Must generate proper arguments for method calls
- Orchestrator provides enough context for intelligent method selection

## Implementation Phases

### Phase 1: Method-Based Tools
- Update Tool interface to expose method lists
- Each method: `{name, description, inputSpec, outputSpec}`
- Start with noteTaker: `addNote()`, `removeNote()`, `listNotes()`

### Phase 2: Enhanced Orchestrator
- Support method selection instead of tool selection
- Generate method arguments from user input
- Enable cyclic operation patterns

### Phase 3: Agent Cycles
- Orchestrator can run multiple cycles per input
- State management between cycles
- Decision-making about when to stop

## Benefits
- Foundation for true "working agent" behavior
- Clear method contracts for LLM reasoning
- Simplified but extensible architecture
- Path to more complex agent behaviors

## Go Structures & Interfaces

### Tool Method System
```go
type Parameter struct {
    Name        string `json:"name"`
    Type        string `json:"type"`        // "string", "int", "bool", "[]Note", etc.
    Description string `json:"description"`
    Required    bool   `json:"required"`
}

type ReturnType struct {
    Type        string `json:"type"`        // "string", "bool", "[]Note", "void", etc.
    Description string `json:"description"`
}

type Method struct {
    Name        string      `json:"name"`
    Description string      `json:"description"`
    Parameters  []Parameter `json:"parameters"`
    ReturnType  ReturnType  `json:"return_type"`
}

type Tool interface {
    Name() string
    Description() string
    Methods() []Method
    Execute(methodName string, args map[string]interface{}) (interface{}, error)
}
```

### LLM Method Selection
```go
type MethodSelection struct {
    ToolName   string                 `json:"tool_name"`
    MethodName string                 `json:"method_name"`
    Arguments  map[string]interface{} `json:"arguments"`
    Reason     string                 `json:"reason"`
}

type AgentContext struct {
    Input            string            `json:"input"`
    State            CycleState        `json:"state"`
    ExecutionHistory []MethodExecution `json:"execution_history"`
}

type LLMService interface {
    DecideWhatToDoNext(context AgentContext, availableTools []Tool) ([]MethodSelection, error)
}
```

### Orchestrator Cycle
```go
type CycleState struct {
    Input       string
    Notes       []Note
    Completed   bool
    Iterations  int
}

type Orchestrator interface {
    ProcessCycle(input string) (*CycleResult, error)
    // Future: ProcessWorkSession(input string) (*WorkResult, error)
}

type MethodExecution struct {
    ToolName      string                 `json:"tool_name"`
    MethodName    string                 `json:"method_name"`
    Arguments     map[string]interface{} `json:"arguments"`
    Result        interface{}            `json:"result"`
    Error         string                 `json:"error,omitempty"`
    ExecutionTime string                 `json:"execution_time"`
}

type CycleResult struct {
    State           CycleState        `json:"state"`
    MethodExecutions []MethodExecution `json:"method_executions"`
    FinalResponse   string            `json:"final_response"`
}
```

### Note Management Tool
```go
type Note struct {
    ID      string    `json:"id"`
    Content string    `json:"content"`
    Created time.Time `json:"created"`
}

type noteTaker struct {
    notes []Note
}

func (n *noteTaker) Methods() []Method {
    return []Method{
        {
            Name: "addNote",
            Description: "Add a new note to the collection",
            Parameters: []Parameter{
                {Name: "content", Type: "string", Description: "The note content", Required: true},
            },
            ReturnType: ReturnType{
                Type: "string", 
                Description: "Generated unique note ID",
            },
        },
        {
            Name: "removeNote", 
            Description: "Remove a note by ID",
            Parameters: []Parameter{
                {Name: "noteId", Type: "string", Description: "ID of note to remove", Required: true},
            },
            ReturnType: ReturnType{
                Type: "bool", 
                Description: "Whether removal succeeded",
            },
        },
        {
            Name: "listNotes",
            Description: "Get all current notes",
            Parameters: []Parameter{}, // No parameters
            ReturnType: ReturnType{
                Type: "[]Note", 
                Description: "Array of all notes",
            },
        },
    }
}
```

### Type System

```go
// Basic type registry - shared across all tools
var PrimitiveTypes = map[string]string{
    "string":   "Text string",
    "int":      "Integer number", 
    "bool":     "Boolean true/false",
    "datetime": "Date and time in ISO format",
    "float":    "Floating point number",
}

type TypeDefinition struct {
    Name   string            `json:"name"`
    Fields []FieldDefinition `json:"fields"`
}

type FieldDefinition struct {
    Name string `json:"name"`
    Type string `json:"type"`  // Either primitive type or custom type name
}

type Tool interface {
    Name() string
    Description() string
    Methods() []Method
    Types() []TypeDefinition  // Tool exposes its custom types
    Execute(methodName string, args map[string]interface{}) (interface{}, error)
}

// noteTaker implementation:
func (n *noteTaker) Types() []TypeDefinition {
    return []TypeDefinition{
        {
            Name: "Note",
            Fields: []FieldDefinition{
                {Name: "ID", Type: "string"},
                {Name: "Content", Type: "string"},
                {Name: "Created", Type: "datetime"},
            },
        },
    }
}
```

**Type Resolution Flow:**
1. LLM sees `[]Note` return type
2. Looks up `Note` in tool's `Types()` 
3. Sees fields with types like `string`, `datetime`
4. Resolves primitives via `PrimitiveTypes` registry
5. Gets full context: "Array of Note objects with ID (text), Content (text), Created (datetime)"

## Orchestrator Cycle Logic

```go
func (o *orchestrator) ProcessCycle(input string) (*CycleResult, error) {
    state := CycleState{
        Input: input,
        Completed: false,
        Iterations: 0,
    }
    
    var executions []MethodExecution
    
    // Agent work loop
    for !state.Completed && state.Iterations < MaxIterations {
        state.Iterations++
        
        // 1. Get all available tools with methods and types
        tools := o.toolService.ListTools()
        
        // 2. Build context with full history
        context := AgentContext{
            Input:            input,
            State:            state,
            ExecutionHistory: executions,
        }
        
        // 3. LLM decides what to do next based on full context
        selections, err := o.llmService.DecideWhatToDoNext(context, tools)
        if err != nil {
            return nil, err
        }
        
        // 4. Execute selected methods and collect results
        for _, selection := range selections {
            execution := o.executeMethod(selection)
            executions = append(executions, execution)
            
            // 5. Update state with execution results
            o.updateState(&state, execution)
        }
        
        // If no methods selected, LLM thinks work is done
        if len(selections) == 0 {
            state.Completed = true
        }
        
        // 6. LLM decides if work is complete
        state.Completed = o.isWorkComplete(context, executions)
    }
    
    return &CycleResult{
        State: state,
        MethodExecutions: executions,
        FinalResponse: o.buildResponse(state, executions),
    }, nil
}

func (o *orchestrator) executeMethod(selection MethodSelection) MethodExecution {
    start := time.Now()
    
    // Get the tool
    tool := o.toolService.GetTool(selection.ToolName)
    if tool == nil {
        return MethodExecution{
            ToolName:      selection.ToolName,
            MethodName:    selection.MethodName,
            Arguments:     selection.Arguments,
            Error:         "Tool not found",
            ExecutionTime: time.Since(start).String(),
        }
    }
    
    // Execute the method
    result, err := tool.Execute(selection.MethodName, selection.Arguments)
    
    execution := MethodExecution{
        ToolName:      selection.ToolName,
        MethodName:    selection.MethodName,
        Arguments:     selection.Arguments,
        Result:        result,
        ExecutionTime: time.Since(start).String(),
    }
    
    if err != nil {
        execution.Error = err.Error()
    }
    
    return execution
}

// MVP Logic: Simple note operations
func (o *orchestrator) updateState(state *CycleState, execution MethodExecution) {
    if execution.Error != "" {
        return // Skip state updates on error
    }
    
    switch execution.ToolName {
    case "noteTaker":
        switch execution.MethodName {
        case "addNote":
            // Result should be noteId (string)
            if noteId, ok := execution.Result.(string); ok {
                // Track that note was added
                log.Printf("Added note with ID: %s", noteId)
            }
        case "removeNote":
            // Result should be success (bool)
            if success, ok := execution.Result.(bool); ok && success {
                log.Printf("Note removed successfully")
            }
        case "listNotes":
            // Result should be []Note
            if notes, ok := execution.Result.([]Note); ok {
                state.Notes = notes // Update state with current notes
            }
        }
    }
}
```