# Input Processing and Categorization Strategy

## Challenge

I have a lot of historical data from JOTTINGS, how do i feed all the messages so that llm can build something useful for me from them?

How to instruct the LLM on what content should be extracted or skipped from user input?

## Approaches

### 1. Dynamic Category Extraction
Use flexible prompts like "extract reasonable categories from this input"

**Pros:**
- Flexible - categories can grow organically over time
- Adapts to new content types automatically

**Cons:**
- Uncontrolled growth - categories may become unwieldy
- Inconsistent categorization

### 2. Predefined Categories
Define fixed categories (personal info, notes, tasks) and instruct LLM to detect only these

**Pros:**
- Easy to control and manage manually
- Consistent categorization
- Predictable behavior

**Cons:**
- Inflexible - new content types require manual category addition
- May miss valuable information that doesn't fit existing categories

### 3. Hybrid Approach
Combine predefined categories with dynamic expansion capabilities

**Process:**
- Start with default category list
- LLM attempts to fit input into existing categories
- When input doesn't fit, LLM suggests new category creation
- Example: "best friends" category suggested when user mentions "my best friend is Dima"

**Pros:**
- Controllable yet flexible
- Grows intelligently with user needs
- Maintains consistency while adapting

**Cons:**
- More complex to implement
- Requires category approval workflow

## 4. Alternative approach


QUESTION:

WHY DO I ACTUALLY NEED TO CATEGORISE THE INPUT?

ANSWER: 

MAYBE I DONT" NEED TO TO IT.

we do it this way instead.
we have tools.
and we create one specific tool that detects the things in the input that could not be disected and handled by other tools, this tool will keep track of such 'unhandled' stuff so that later i can review the list and add a new tool if needed. 
it means that this tool has somehow understand what is 'unhandled'. 

With this light maybe what we call tools are not tools at all, but rather modules.
Modules can handle input and contribute to the profile. For example. Spanish learning extension would handle text and extract some new vocabular and build list of new vocabulary. And it would extend the profile by adding something like 

```json

profileExtension: 
{
    context: "I'm learnig spanish.",
    data: {
        vocabulary: ["casa", "coche", "me voy a ir"]
    }
}
```

So instead of 
```golang
type Tool interface {
	Execute(input string, context Context) (string, error)
	Name() string
	Description() string
}
```

we'll hae something like 

```golang
type ProfileExtension struct {
    Context: string
    Data: /// custom object  
}

type Module interface {
	Name() string
    Description() string
    HandleInput(input string, context Context) (string, error)
	GetProfileExtension() *ProfileExtension
```

Module might or might not extend a profile. For example time module remains a simple module that doesn't contribute to the profile anythign. But spanish module will maintain a list of vocabulary and provide ProfileExtension that will contain this list.

q1. The question is what happens when the list of vocabualry grops to 10k words... in this case maybe module should provide also a list of tools to, say pick a word, add a word, and so on ....

q2. next question is do we allow tools and modules to use llm internally or not? maybe orchestrator should be the only 'brain' in the system and the rest of the system should be built in a way taht would allow orchestrator to make all the decicions ...

we need to find this boundary bettween modules and orchestrator. 


LEt's list some use cases and try to find some system taht will handle all of them and also be extendable:

all the use cases will be in the format of INPUT and RESULT
1.
INPUT: 'how do i say hello in spanish'
RESULT: 'profile gets information that i'm learning spanish and a this word 'hello' gets added to the list'

2. 
INPUT: 'start upwork with $30 per hour'
RESULT: this is added to 'todo list' as actionable item

3. 
INPUT: 'да конечно отказ от мелодии немножко меня подкосил но это все лишь говорит о том что ну как подкосил я чувствую такое какое разочарование вот хотя это просто быть одна вакансии заднего из миллиардов и почему это влияет на мою какой сам уверенность не понимаю значит какие выводы нам нужно сделать рутину более стабильную и сдать список всех сайтов и откликаться браузер все вакансии ради времени все может быть даже агентом лиц и своей стороны я не знаю ну короче ну просто нужно больше значит ресурс инвестировать все больше работать очень просто туча так что давайте ребята и башня' 
RESULT: this text is reduced to the key idea 'don't focus on failures, learn the lesson, fix mistakes, move forward' and added to the list 'mindset'

4. 
INPUT:  Еще кстати момент. Вчера наелся меда с сыром. Ой, много прям мяса, апельсинов. Сегодня спал хорошо 8,5 часов.
RESULT: it's recognized as 'observation' and goes to the 'recommendatins' or mayebe 'insights' list


5. 'need to call dima tonight' goes as actionable item and goes to todo list

How would it change orchestrator? 
Here's how:



module exposes description of when it should be invoked
module exposes a list of tools that orchestrator can invoke 
module explses a profile extension

one module's work can be enhanced if it knows something that other module might have, for example if there is a module that tracks my interests and expoeses them, then the module that generates spanish texts might use this info to create a text taht is going to be more relevant to me.
or maybe one module might want to call another module's tool....


it's like common context


TOOLS vs MODULES?

EXAMPLE OF TOOLS:
- browse the internet
- add event to calendar
- take a note
- 

EXAMPLE OF MODULES:

- spanish

CAN MODULE BE dynamic?
for example i want to add a new module by providing a custom instruction, i'm sending, "hey, i want you to track spanish words".
orchestrator will treat such request as a reuqest to add a new 'module/custom instruction' and will create a module that will extend prfile by adding info that 
1. i'm learning spanish
2. second it will use note taking tool to check current notes section and will udpate/add the section called spanish vocabulary
3. 
this will create a new module for orchestrator, so that it will understand that it has to use the "NOTE TRACKER TOOL" to take a note in 'my..



IDEA: strip the entire architecture down to architector and one essential tool: "noteTaker" with several key methods that will allow it to add or remove a note.
then orchestrator will handle each input in a way that structures the input, normalises it and either adds a note or removes it from the list.

and then we'll have custom instructions....


