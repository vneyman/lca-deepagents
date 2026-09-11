from deepagents import create_deep_agent

from models import model, strong_model

agent = create_deep_agent(model=strong_model, name="Scratch_Agent")

result = agent.invoke({"messages": [{"role": "user", "content": "What is an LLM?"}]})

print(result["messages"][-1].content)

# use with gpt-5.6 models
# print(result["messages"][-1].content[0]['text'])
