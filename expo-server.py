import modal
import subprocess
import asyncio

image = (
    modal.Image.debian_slim()
        .apt_install("nodejs")
        .apt_install("npm")
        .run_commands("echo swag")
        .run_commands("rm -rf $(npm root -g)")
        .run_commands("npm cache clear -g --force")
        .run_commands("npm install -g npx")
        .run_commands("npm install -g ngrok")
        .run_commands("npm install -g expo")
        .run_commands("npx create-expo-app@latest -y app")
        .run_commands("cd app")
)

# app = modal.App.lookup("expo-server", create_if_missing=True)
app = modal.App("expo-new")

async def start_server():
    with modal.enable_output():
        print("Creating sandbox")
        sb = await modal.Sandbox.create.aio(app=app, image=image)
        print("Starting expo devserver")
        p = await sb.exec.aio("npx", "expo", "start", "--tunnel")
        # p = await sb.exec.aio("echo", "hello from container")
        if p.stderr:
            print("Error:")
            async for line in p.stderr:
                print(line, end="")
        
        async for line in p.stdout:
            print(line, end="")

        await p.wait.aio()
        await sb.terminate.aio()

@app.local_entrypoint()
def main():
    asyncio.run(start_server())
