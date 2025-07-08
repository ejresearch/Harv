import requests

BASE_URL = "http://127.0.0.1:8000"

def register():
    print("📝 Registering…")
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "test@example.com",
        "password": "password",
        "name": "Test User",
        "onboarding_data": "Test data"
    })
    print(r.status_code, r.text)
    return r.json().get("user_id") if r.status_code == 200 else None

def login():
    print("🔑 Logging in…")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    print(r.status_code, r.text)
    return r.json().get("user_id") if r.status_code == 200 else None

def get_modules():
    print("📚 Fetching modules…")
    r = requests.get(f"{BASE_URL}/modules")
    print(r.status_code, r.text)
    if r.status_code == 200 and r.json():
        return r.json()[0]['id']
    return None

def chat(user_id, module_id):
    print("💬 Starting chat…")
    r = requests.post(f"{BASE_URL}/chat", json={
        "user_id": user_id,
        "module_id": module_id,
        "message": "Hello!"
    })
    print(r.status_code, r.text)

def save_summary(user_id, module_id):
    print("📝 Saving summary…")
    r = requests.post(f"{BASE_URL}/memory/summary", json={
        "user_id": user_id,
        "module_id": module_id,
        "what_learned": "Basics of mass comm",
        "how_learned": "By chatting"
    })
    print(r.status_code, r.text)

def edit_summary(user_id, module_id):
    print("✏️ Editing summary…")
    r = requests.post(f"{BASE_URL}/memory/edit", json={
        "user_id": user_id,
        "module_id": module_id,
        "what_learned": "Updated what I learned"
    })
    print(r.status_code, r.text)

def history(user_id, module_id):
    print("🕒 Fetching conversation history…")
    r = requests.post(f"{BASE_URL}/conversation/history", json={
        "user_id": user_id,
        "module_id": module_id
    })
    print(r.status_code, r.text)

def export_conversation(user_id, module_id):
    print("📄 Exporting conversation…")
    r = requests.post(f"{BASE_URL}/export", json={
        "user_id": user_id,
        "module_id": module_id
    })
    print(r.status_code, r.text)

def reset_memory(user_id, module_id):
    print("🧹 Resetting memory…")
    r = requests.post(f"{BASE_URL}/memory/reset", json={
        "user_id": user_id,
        "module_id": module_id
    })
    print(r.status_code, r.text)

if __name__ == "__main__":
    user_id = login()
    if not user_id:
        user_id = register()
    if not user_id:
        print("❌ Could not login or register.")
        exit(1)

    module_id = get_modules()
    if not module_id:
        print("❌ No modules found.")
        exit(1)

    chat(user_id, module_id)
    save_summary(user_id, module_id)
    edit_summary(user_id, module_id)
    history(user_id, module_id)
    export_conversation(user_id, module_id)
    reset_memory(user_id, module_id)
