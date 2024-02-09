from typing import Union

from fastapi import FastAPI
from main_parser import ParserScript

app = FastAPI()


@app.get("/")
async def root():
    parse_script = ParserScript();
    parse_script.main();
    return {"message": "Hello World"}