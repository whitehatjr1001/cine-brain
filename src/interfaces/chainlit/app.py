# app.py
from chainlit import app
from src.graph.graph import graph

@app.on_message
async def main(message: str):
    await graph.invoke(message)
