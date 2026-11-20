"""Runs the API: python -m jean_cours"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("jean_cours.api.app:app", host="0.0.0.0", port=8000)
