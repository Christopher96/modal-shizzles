import requests

r = requests.get("http://localhost:4040/api/tunnels")
data = r.json()
for tunnel in data["tunnels"]:
    print(tunnel["public_url"])
