import subprocess
import threading

row = 5
width = 400
height = 330

def Call(i):
    subprocess.call(f"python GameClient.py {(i % row) * width} {(i // row) * height + 30}")
def CallServer():
    subprocess.call("python GameServer.py")

if(__name__ == "__main__"):
    tr = []
    t = threading.Thread(target=CallServer)
    t.start()
    for i in range(15):
        t = threading.Thread(target=Call, args=(i,))
        t.start()
        tr.append(t)
    for t in tr:
        t.join()