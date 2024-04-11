import tornado.ioloop
import tornado.web
import tornado.websocket
import Model
import numpy as np

dqn = Model.DQN(10, 2, fileName="")

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        return
        print("WebSocket opened")

    def on_message(self, message):
        m = message.split(":")
        if(m[0] == "A"):
            list = [float(i) for i in m[1].split(",")]
            self.write_message("A:" + str(dqn.ChooseAction(np.reshape(list, [10, 1]))))
        if(m[0] == "B"):
            args = m[1].split(";")
            state = [float(i) for i in args[0].split(",")]
            ac = int(args[1])
            reward = float(args[2])
            nextState = [float(i) for i in args[3].split(",")]
            d = (args[4] == 1)
            dqn.Remember(np.reshape(state, [10, 1]), ac, reward, np.reshape(nextState, [10, 1]), d)
            pass 
        if(m[0] == "C"):
            self.write_message("C:" + str(dqn.epsilon))

    def on_close(self):
        return
        print("WebSocket closed")

def make_app():
    return tornado.web.Application([
        (r"/websocket", WebSocketHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    print("WebSocket server started on port 5000")
    tornado.ioloop.IOLoop.current().start()
