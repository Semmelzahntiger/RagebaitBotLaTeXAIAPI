import uvicorn
from fastapi import FastAPI, Request, Response, UploadFile, File, Form
from PIL import Image

import io

from sympy.parsing.latex import parse_latex
from texteller import load_model, load_tokenizer, img2latex
import numpy as np
import re
from sympy import simplify

app = FastAPI()

model = load_model()
tokenizer = load_tokenizer()

@app.post("/prove")
async def prove(token: str = Form(...), img: UploadFile = File(...), ans: str = Form(...)):
    image_bytes = await img.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_array = np.array(image)
    latex = img2latex(model, tokenizer , [image_array])[0]
    stripped_interpreted = strip(latex)
    stripped_answer = strip(ans)
    try:
        correct = equalLatex(stripped_interpreted, stripped_answer)
        return {"token": token, "correct": correct, "exception" : False}
    except Exception as e:
        print("Error" + str(e))
        return {"token": token, "correct": False, "exception" : True}
@app.post("/interpret")
async def interpret(img: UploadFile = File(...)):
    image_bytes = await img.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_array = np.array(image)
    latex = img2latex(model, tokenizer, [image_array])[0]
    stripped_latex = strip(latex)
    return {"interpreted": stripped_latex}

def strip(latex: str) -> str:
    latex.strip()
    latex = re.sub(r'^\\\[(.*)\\]$', r'\1', latex, flags=re.DOTALL)
    latex = re.sub(r'^\$\$(.*)\$\$$', r'\1', latex, flags=re.DOTALL)
    latex = re.sub(r'^\$(.*)\$$', r'\1', latex, flags=re.DOTALL)
    return latex.strip()

def equalLatex(latex1: str, latex2: str) -> bool:
    expr1 = parse_latex(latex1)
    expr2 = parse_latex(latex2)
    print(expr1, expr2)
    return simplify(expr1 - expr2) == 0

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7779)