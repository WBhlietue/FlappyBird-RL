import numpy as np
import random
import json


class Replay:
    def __init__(self):
        self.replays = []

    def Add(self, state, action, reward, next, done):
        self.replays.append((state, action, reward, next, done))

    def Sample(self, size):
        datas = random.sample(self.replays, size)
        (state, action, reward, next, done) = zip(*datas)
        return np.array(state), action, reward, np.array(next), done

    def Size(self):
        return len(self.replays)


class NN:
    def __init__(self, outputSize, inputSize, learningRate=0.001):
        self.outputSize = outputSize
        self.inputSize = inputSize
        self.hidden = []
        self.hiddenWidth = inputSize
        self.learning_rate = learningRate

    def AddHidden(self, nodeNum):
        # hidden = []
        # for i in range(self.hiddenWidth):
        #     arr = [0.01 for _ in range(nodeNum)]
        #     hidden.append(arr)
        # hidden = np.array(hidden)
        # self.hidden.append(hidden)
        self.hidden.append(np.random.normal(size=(self.hiddenWidth, nodeNum))/10000)
        self.hiddenWidth = nodeNum

    def AddOutput(self):
        self.output = np.random.normal(
            size=(self.hiddenWidth, self.outputSize))

    def Relu(self, x):
        return np.maximum(0, x)

    def Calculate(self, input):
        current = input.T
        for i in self.hidden:
            current = np.dot(current, i)
            current = self.Relu(current)
        output = np.dot(current, self.output)
        return output

    def Save(self, fileName):
        h = []
        for i in self.hidden:
            h.append(i.tolist())
        data = {
            "hidden": h,
            "output": self.output.tolist()
        }
        file = open(fileName, "w")
        json.dump(data, file)

    def Load(self, fileName):
        file = open(fileName, "r")
        data = json.load(file)
        self.hidden = data["hidden"]
        self.output = np.array(data["output"])

    def GetWeight(self):
        return [self.hidden, self.output]

    def SetWeight(self, data):
        self.hidden = data[0]
        self.output = data[1]

    

    def Optimize(self, states, target_Qs, learning_rate=0.001):
        
        for i in range(len(states)):
            state = states[i]
            target_Q = target_Qs[i]
            current_Q = self.Calculate(state)
            # print(target_Q, current_Q)
            loss_gradient = -2 * (target_Q - current_Q) 

            output_gradient = np.dot(loss_gradient, self.output.T)  
            self.output -= learning_rate * output_gradient.T
            hidden_gradient = np.dot(self.output, loss_gradient.T)
            for j in range(len(self.hidden) - 1, 0, -1):
                hidden_gradient = np.dot(self.hidden[j],hidden_gradient)
                self.hidden[j] -= learning_rate * hidden_gradient
                # break

            self.hidden[0] -= learning_rate * np.dot(state, hidden_gradient.T)




class DQN:
    def __init__(self, inputSize, outputSize, batch_size=128, gamma=0.9, epsilon=1, epsilonDecay=0.9999, epsilonMin=0.01, updateFreq=20, fileName=""):
        self.outputSize = outputSize
        self.inputSize = inputSize
        if(len(fileName) == 0):
            self.model = self.CreateModel()
            self.targetModel = self.CreateModel()
        else:
            self.model = NN(self.outputSize, self.inputSize)
            self.targetModel = NN(self.outputSize, self.inputSize)
            self.model.Load(fileName)
            self.targetModel.Load(fileName)
        self.reward = Replay()
        self.batch_size = batch_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilonDecay = epsilonDecay
        self.epsilonMin = epsilonMin
        self.updateFreq = updateFreq
        self.step = 0

    def CreateModel(self):
        model = NN(self.outputSize, self.inputSize)
        model.AddHidden(128)
        model.AddHidden(64)
        model.AddOutput()
        return model

    def Train(self):
        if (self.batch_size > self.reward.Size()):
            return
        states, actions, rewards, next_states, dones = self.reward.Sample(
            self.batch_size)
        target_Qs = []
        for i in range(self.batch_size):
            if dones[i]:
                target_Qs.append(rewards[i])
            else:
                target = rewards[i] + self.gamma * \
                    np.max(self.targetModel.Calculate(next_states[i]))
                target_Qs.append(target)
        current_Qs = []
        for i in states:
            current_Qs.append(self.model.Calculate(i))
        self.model.Optimize(np.array(states), np.array(target_Qs))
        if self.step % self.updateFreq == 0:
            weight = self.model.GetWeight()
            self.targetModel.SetWeight(weight)
            self.model.Save("Model.json")
        self.step += 1

    def Predict(self, state):
        return self.targetModel.Calculate(state)

    def UpdateTarget(self):
        weight = self.model.GetWeight()
        self.targetModel.SetWeight(weight)

    def Remember(self, state, action, reward, next_state, done):
        self.reward.Add(state, action, reward, next_state, done)
        self.Train()

    def ChooseAction(self, state):
        a = 0
        if np.random.rand() <= self.epsilon:
            a = np.random.choice(self.outputSize)
        else:
            q_values = self.Predict(state)
            a = np.argmax(q_values[0])
        self.epsilon = max(self.epsilon * self.epsilonDecay, self.epsilonMin)
        return a