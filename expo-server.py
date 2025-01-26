import modal
import subprocess
import os

image = (
    modal.Image.debian_slim()
        .pip_install("rich")
        .apt_install("nodejs")
        .apt_install("npm")
        .run_commands("npm install create-expo-app -g")
        .run_commands("create-expo-app -y app")
        .workdir("/app")
        .run_commands("npm install expo")
        .run_commands("npm install @expo/ngrok")
        .run_commands("npm install expo-blur@14.0.3")
        .run_commands("npm i")
)

# app = modal.App.lookup("expo-server", create_if_missing=True)
# app = modal.App("expo-new")
app = modal.App("expo-new", image=image)

@app.function()
def start_server():
    with modal.enable_output():
        p = subprocess.Popen("npm run start", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        while True:
            line = p.stdout.readline().decode("utf-8")
            print(line)
            if "Logs" in line:
                print("pressing c")
                output, error = p.communicate(input=b'c\n')
                p.stdin.close()
                print(error)
                print(output)

            if not line:
                break

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

@app.local_entrypoint()
def main():
    start_server.remote()



# p = sb.exec("npx", "expo", "-v")
# print(p.stdout.read())
# p = sb.exec("node", "-v")
# print(p.stdout.read())
# p = sb.exec("npm", "-v")
# print(p.stdout.read())
# p = sb.exec("npx", "-v")
# print(p.stdout.read())
