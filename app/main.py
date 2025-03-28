from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

def main():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
