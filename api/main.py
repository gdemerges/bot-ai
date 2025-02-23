from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API déployée sur Azure 🚀"}

@app.get("/ping")
def ping():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)