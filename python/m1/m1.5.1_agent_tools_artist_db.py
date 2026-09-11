import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
from pathlib import Path

from deepagents import create_deep_agent
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool

from models import model, strong_model

DB_PATH = Path(__file__).parent.parent / "db" / "artist.db"
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

SYSTEM_PROMPT = """You are a SQL analyst with access to an artist database.

Rules:
- Use read_sql for SELECT queries.
- Do not modify the database.
- If a tool returns an error, revise the SQL and try again.
- Show your SQL in your final answer.
"""

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "artist_schema.sql"
SCHEMA = SCHEMA_PATH.read_text(encoding="utf-8")
READ_SQL_DESCRIPTION = f"""Run a read-only SELECT query against the artist database.

The current database schema is:

```sql
{SCHEMA}
```
"""

@tool(description=READ_SQL_DESCRIPTION)
def read_sql(query: str) -> str:
    """Run a read-only SELECT query against the artist database."""
    try:
        return str(db.run(query))
    except Exception as e:
        return f"Error: {e}"


agent = create_deep_agent(
    model=strong_model,
    name="SQL_Agent",
    tools=[read_sql],
    system_prompt=SYSTEM_PROMPT,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Which artist sold the most albums in total?"}]}
)

print(result["messages"][-1].content)
