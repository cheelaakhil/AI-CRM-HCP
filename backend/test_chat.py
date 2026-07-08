import requests

try:
    res = requests.post("http://localhost:8000/api/chat", json={
        "message": "I want to log a new interaction",
        "conversation_history": []
    })
    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)
except Exception as e:
    print("ERROR:", e)
