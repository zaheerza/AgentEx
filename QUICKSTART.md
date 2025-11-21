# Quick Start Guide

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your API key:**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

   Or create a `.env` file:
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ```

## Running the Examples

### Simple Agent
The basic autonomous agent that can use tools:

```bash
cd examples
python simple_agent.py
```

**What it does:**
- Reads and writes files
- Performs calculations
- Lists directories
- Demonstrates the core agent loop

### Research Agent
An agent that researches topics and creates reports:

```bash
python research_agent.py
```

**What it does:**
- Searches for information (simulated)
- Takes research notes
- Synthesizes findings
- Generates structured reports

### Code Development Agent
An agent that writes, tests, and debugs code:

```bash
python code_agent.py
```

**What it does:**
- Writes code based on specifications
- Runs and tests code
- Debugs errors iteratively
- Produces working solutions

## Modifying the Examples

### Change the task:
In each example file, find the `main()` function and modify the task/specification:

```python
# simple_agent.py
task = "Your custom task here"

# research_agent.py
agent.research("Your research topic", depth="comprehensive")

# code_agent.py
specification = """
Your development specification here
"""
```

### Add new tools:
In the `_define_tools()` method, add your tool definition:

```python
{
    "name": "my_custom_tool",
    "description": "What this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param_name"]
    }
}
```

Then implement it in `_execute_tool()`:

```python
def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
    if tool_name == "my_custom_tool":
        # Your implementation
        return "Result"
```

## Understanding the Agent Loop

All agents follow this pattern:

```
1. User provides a task
   ↓
2. Agent reasons about the task
   ↓
3. Agent decides to use a tool
   ↓
4. Tool is executed, result returned
   ↓
5. Agent reflects on the result
   ↓
6. Back to step 2 (or complete if done)
```

## Best Practices

1. **Start Simple**: Begin with basic tasks and gradually increase complexity

2. **Monitor Iterations**: Keep an eye on the iteration count to prevent infinite loops

3. **Set Token Limits**: Control costs by limiting max_tokens

4. **Error Handling**: Always wrap tool execution in try-catch blocks

5. **Testing**: Test your tools independently before giving them to the agent

6. **Safety**:
   - Sandbox code execution
   - Validate file paths
   - Limit API calls
   - Review agent actions

## Common Issues

### "Max iterations reached"
- Task is too complex
- Agent is stuck in a loop
- Increase max_iterations or simplify the task

### API Key errors
- Ensure ANTHROPIC_API_KEY is set correctly
- Check your API key has proper permissions

### Tool execution failures
- Check tool implementation
- Verify file paths and permissions
- Add better error messages

## Next Steps

1. **Read the full README.md** for in-depth explanations

2. **Experiment with different tasks** to see how the agent adapts

3. **Build your own agent** for a specific use case

4. **Combine multiple agents** for complex workflows

5. **Add real integrations** (databases, APIs, services)

## Resources

- [Anthropic Documentation](https://docs.anthropic.com)
- [Claude API Reference](https://docs.anthropic.com/api)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/tool-use)

## Need Help?

- Check the examples for reference implementations
- Review the tool definitions and execution logic
- Start with simpler tasks and build up complexity
- Monitor the agent's reasoning output to debug issues
