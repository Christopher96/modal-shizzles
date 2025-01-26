from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from contextlib import asynccontextmanager
import httpx


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient(base_url='http://127.0.0.1:4040/') as client:
        yield {'client': client}
        # The Client closes on shutdown 


app = FastAPI(lifespan=lifespan)


async def _reverse_proxy(request: Request):
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


app.add_route('/{path:path}', _reverse_proxy, ['GET', 'POST'])


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
