import modal
import httpx
import subprocess
import requests
import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from contextlib import asynccontextmanager

image = (
    modal.Image.debian_slim()
        .pip_install("fastapi[standard]", "pydantic", "rich", "requests")
        .apt_install("nodejs", "npm", "net-tools")
        .run_commands("npm install create-expo-app -g")
        .run_commands("create-expo-app -y app")
        .workdir("/app")
        .run_commands("npm install expo")
        .run_commands("npm install @expo/ngrok")
        .run_commands("npm install expo-blur@14.0.3")
        .run_commands("npm i")
)

app = modal.App("expo-proxy", image=image)


# Create a persisted dict - the data gets retained between app runs
global_dict = modal.Dict.from_name("global_dict", create_if_missing=True)

@app.function()
def start_server():
    with modal.enable_output():
        # print("Creating sandbox")
        # sb = modal.Sandbox.create(app=app, image=image, unencrypted_ports=[4040])
        # p = sb.exec("npx", "expo", "start", "--tunnel")
        #
        # for line in p.stdout:
        #     print(line, end="")
        #     if "Logs" in line:
        #         break
        #
        #
        # time.sleep(2)
        # print("Forwarding port")
        # tunnel = sb.tunnels()[4040]
        #
        # global_dict["target_host"] = tunnel.unencrypted_host
        # global_dict["target_port"] = tunnel.unencrypted_port
        #
        # print(f"{tunnel.url}")
        # print(f"http://{tunnel.unencrypted_host}:{tunnel.unencrypted_port}")
        #
        # p2 = sb.exec("netstat", "-tlpn")
        #
        # for line in p2.stdout:
        #     print(line, end="")
        #
        # p.wait()
        # sb.terminate()

        p = subprocess.Popen("npx expo start --tunnel", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        while True:
            line = p.stdout.readline().decode("utf-8")
            print(line)
            if "Logs" in line:
                subprocess.run(["netstat", "-tlpn"])
                r = requests.get("http://127.0.0.1:4040/api/tunnels")
                data = r.json()
                for tunnel in data["tunnels"]:
                    print(tunnel["public_url"])

                # print(f"{tunnel.url}")
                # print(f"http://{tunnel.unencrypted_host}:{tunnel.unencrypted_port}")

            if not line:
                break


@app.local_entrypoint()
def main():
    global_dict["target_host"] = "127.0.0.1"
    global_dict["target_port"] = "4040"
    start_server.remote()

@asynccontextmanager
async def lifespan(app: FastAPI):
    target_url = f'http://{global_dict["target_host"]}:{global_dict["target_port"]}/'
    print(target_url)

    async with httpx.AsyncClient(base_url=target_url) as client:
        yield {'client': client}

web_app = FastAPI(lifespan=lifespan)

async def _reverse_proxy(request: Request):
    print("Request")
    client = request.state.client
    url = httpx.URL(path=request.url.path, query=request.url.query.encode('utf-8'))
    headers = [(k, v) for k, v in request.headers.raw if k != b'host']
    req = client.build_request(
        request.method, url, headers=headers, content=request.stream()
    )
    r = await client.send(req, stream=True)
    return StreamingResponse(
        r.aiter_raw(),
        status_code=r.status_code,
        headers=r.headers,
        background=BackgroundTask(r.aclose)
    )


web_app.add_route('/{path:path}', _reverse_proxy, ['GET', 'POST'])

@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app




# print("Creating sandbox")
# sb = modal.Sandbox.create(app=app, image=image)
# print("Starting expo devserver")
# p = sb.exec("npx", "expo", "start", "--tunnel")
#
# for line in p.stdout:
#     print(line, end="")
#
# p.wait()
# sb.terminate()
