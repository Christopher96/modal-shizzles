import modal
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx
import uvicorn
import subprocess

image = modal.Image.debian_slim().pip_install("fastapi[standard]", "pydantic")
app = modal.App("socket-proxy", image=image)

web_app = FastAPI()

target_url = "localhost"
target_port = "8081"

@web_app.get("/{path:path}")
async def proxy_get(request: Request, path: str, scheme: str = "http"):
    url = f"{scheme}://{target_url}:{target_port}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=request.headers, params=request.query_params)
    return HTMLResponse(content=response.text, status_code=response.status_code)

@web_app.post("/{path:path}")
async def proxy_post(request: Request, path: str, scheme: str = "http"):
    url = f"{scheme}://{target_url}:{target_port}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=request.headers, params=request.query_params, body=request.body)
    return HTMLResponse(content=response.text, status_code=response.status_code)

# if __name__ == "__main__":
#     uvicorn.run("http-proxy:app", host="0.0.0.0", port=8000, log_level="info")

@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app


