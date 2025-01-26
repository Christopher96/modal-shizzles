import modal
import httpx
import subprocess
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from contextlib import asynccontextmanager
import time

image = (
    modal.Image.debian_slim()
        .pip_install("fastapi[standard]", "pydantic", "rich")
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

@app.function()
def start_server():
    with modal.enable_output():
        # print("Creating sandbox")
        # sb = modal.Sandbox.create(app=app, image=image, unencrypted_ports=[4040])
        # print("Starting expo devserver")
        # p = sb.exec("npx", "expo", "start", "--tunnel")
        #
        # for line in p.stdout:
        #     print(line, end="")
        #     if "Logs" in line:
        #         break
        #
        # p2 = sb.exec("netstat", "-tlpn")
        #
        # for line in p2.stdout:
        #     print(line, end="")
        #
        # time.sleep(2)
        # print("Forwarding port")
        # tunnel = sb.tunnels()[4040]
        #
        # print(f"{tunnel.url}")
        # print(f"http://{tunnel.unencrypted_host}:{tunnel.unencrypted_port}")
        #
        # p.wait()
        # sb.terminate()

        with modal.forward(8081, unencrypted=True) as tunnel:
            p = subprocess.Popen("npx expo start -g", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            while True:
                line = p.stdout.readline().decode("utf-8")
                print(line)
                if "Logs" in line:
                    subprocess.run(["netstat", "-tlpn"])
                    print(f"{tunnel.url}")
                    print(f"http://{tunnel.unencrypted_host}:{tunnel.unencrypted_port}")

                if not line:
                    break


@app.local_entrypoint()
def main():
    start_server.remote()

#
# target_host = "127.0.0.1"
# target_port = "4040"
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with httpx.AsyncClient(base_url=f'http://{target_host}:{target_port}/') as client:
#         yield {'client': client}
#         # The Client closes on shutdown 
#
# web_app = FastAPI(lifespan=lifespan)
#
# async def _reverse_proxy(request: Request):
#     subprocess.run(["netstat", "-tlpn"], shell=True)
#
#     client = request.state.client
#     url = httpx.URL(path=request.url.path, query=request.url.query.encode('utf-8'))
#     headers = [(k, v) for k, v in request.headers.raw if k != b'host']
#     req = client.build_request(
#         request.method, url, headers=headers, content=request.stream()
#     )
#     r = await client.send(req, stream=True)
#     return StreamingResponse(
#         r.aiter_raw(),
#         status_code=r.status_code,
#         headers=r.headers,
#         background=BackgroundTask(r.aclose)
#     )
#
#
# web_app.add_route('/{path:path}', _reverse_proxy, ['GET', 'POST'])
#
# @app.function()
# @modal.asgi_app()
# def fastapi_app():
#     return web_app
#



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
