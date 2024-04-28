from fastapi import FastAPI, Body
import os.path
import time

app = FastAPI()

@app.get("/")
def home():
    return {"Ok!"}

@app.post("/question/")
def get_answer(data=Body()):
    text = str(data["question"])
    l = 0 if text is None else len(text)
    if l < 5:
        return {"msg": f"Введен неинформативный вопрос. Пожалуйста, напишите подробнее!"}
    print("Question: ", text)
    with open('question.txt', 'w') as f:
        f.write(text)
    while True:
        if os.path.exists('answer.txt'):
            break
        time.sleep(0.01)
    with open('answer.txt', 'r') as f:
        answer = f.read()
    print("Answer: ", answer)
    os.remove('answer.txt')
    return {"msg": answer}




