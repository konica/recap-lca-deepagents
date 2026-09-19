# python/m2/m2.4_homework.py
"""M2.4 Homework: Ask Your Own Question, Then Grade It.

THE IDEA
Lab 2 asked one fixed, dependent-query question about the Chinook
database and let the interpreter chain four SQL queries together inside
a single eval() call. This homework asks you to pose your OWN question
about the database (anything query_chinook and a little JavaScript can
answer, simple or dependent, your call), and then, since this lesson is
also about evaluating what an agent's code produces, write your own quick
eval check that judges whether the agent's answer looks right. There's no
single right question or eval method here, that's the point.

WHAT YOU FILL IN
  TODO 1: write your own natural-language question about the Chinook
    database (see the schema hints in SYSTEM below) for the interpreter
    agent to answer using eval() and query_chinook.
  TODO 2: write a small eval_answer(...) function that independently
    checks whether the agent's final answer looks correct. However you
    want to do this is fine: run your own SQL query and compare, check
    for an expected keyword or number, or just print both side by side
    for your own judgment call. Pick whatever level of rigor makes sense
    for your question.

RUN
  cd python
  uv run ./m2/m2.4_homework.py
"""

import json
import sqlite3
import uuid
from pathlib import Path

from deepagents import create_deep_agent
from langchain.tools import tool
from langchain_quickjs import CodeInterpreterMiddleware

from models import model

DB_PATH = Path(__file__).resolve().parent / "chinook.db"

SYSTEM = (
    "You are a sales analyst for Chinook Digital Music Store. "
    "Use the query_chinook tool to query the database. "
    "Key tables: Artist(ArtistId, Name), Album(AlbumId, Title, ArtistId), "
    "Track(TrackId, Name, AlbumId, GenreId), Genre(GenreId, Name), "
    "Customer(CustomerId, FirstName, LastName, Country), "
    "Invoice(InvoiceId, CustomerId), "
    "InvoiceLine(InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity). "
    "Revenue is InvoiceLine.UnitPrice * InvoiceLine.Quantity. "
    "The eval tool supports Programmatic Tool Calling (PTC): JavaScript "
    "running inside eval() can call query_chinook via tools.queryChinook()."
)


@tool
def query_chinook(sql: str) -> str:
    """Execute a read-only SQL query against the Chinook database. Returns a JSON-encoded string."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(sql)
        rows = [dict(row) for row in cursor.fetchall()]
        return json.dumps(rows)
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════
# TODO 1: Write your own question about the Chinook database.
#
# Pick anything the query_chinook tool can answer: top customers by
# country, which artist has the most albums, average invoice total by
# year, whatever you're curious about. A question with a couple of
# dependent steps (like Lab 2's) is a good excuse to use PTC, but a
# single-query question is a perfectly fine answer too.
# ════════════════════════════════════════════════════════════════════════

TASK = """
You need to do the following sub tasks.
1. Retrieve the top 5 customers who have the largest total sum of all their invoices. 
The result should include the customer's ID, first name, last name, and the total amount of their invoices.
2. Retrieve the top 5 customers based on the total amount of their invoices. 
The result should include the customer's ID, first name, last name, and the total amount of each invoice. 
Note that this query will return one invoice amount per customer, and the results will be ordered by the invoice total in descending order.
3. Determine which customers satisify both sub tasks above.
"""  # TODO 1: replace with your own question


# ════════════════════════════════════════════════════════════════════════
# TODO 2: Write a simple eval check for the agent's answer.
#
# eval_answer(answer_text) runs after the agent responds. Independently
# work out what you believe the right answer is (run your own SQL query,
# do the math by hand, whatever) and compare it against answer_text. Print
# whatever verdict makes sense; this doesn't need to be a strict
# pass/fail, a reasoned printout is fine.
# ════════════════════════════════════════════════════════════════════════

def eval_answer(answer_text: str) -> None:
    return {
        "sub-task-1": """6	Helena	Holý	49.62
26	Richard	Cunningham	47.62
57	Luis	Rojas	46.62
45	Ladislav	Kovács	45.62
46	Hugh	O'Reilly	45.62""",
        "sub-task-2": """
23	John	Gordon	13.86
6	Helena	Holý	8.91
10	Eduardo	Martins	8.91
14	Mark	Philips	8.91
27	Patrick	Gray	8.91
"""

    }


if TASK is None:
    raise NotImplementedError("TODO 1: see the comment block above")

agent = create_deep_agent(
    model=model,
    tools=[query_chinook],
    middleware=[CodeInterpreterMiddleware(ptc=["query_chinook"])],
    system_prompt=SYSTEM,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": TASK}]},
    config={"configurable": {"thread_id": str(uuid.uuid4())}},
)

answer = result["messages"][-1].content
print(answer)
eval_answer(answer)
