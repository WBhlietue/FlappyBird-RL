from collections import deque
import numpy as np
import random
import NN


class Replay:

    def __init__(self, maxLen=10000):
        self.replays = deque(maxlen=maxLen)

    def Add(self, state, action, reward, next, done):
        self.replays.append((state, action, reward, next, done))
        # if(len(self.replays) > 10000):
        #     self.replays.pop(0)

    def Sample(self, size):
        datas = random.sample(self.replays, size)
        return datas
        # (state, action, reward, next, done) = zip(*datas)
        # reward = np.reshape(reward, (len(reward), 1))
        # return np.array(state), action, (reward), np.array(next), done

    def Size(self):
        return len(self.replays)


class DQN:

    def __init__(self,
                 inputSize,
                 outputSize,
                 batch_size=32,
                 gamma=0.99,
                 epsilon=1,
                 epsilonDecay=0.999,
                 epsilonMin=0.01,
                 updateFreq=20,
                 fileName="",
                 train=True,
                 saveFreq=100,
                 maxLen=10000, 
                 saveName = "modelSave.txt", 
                 name = ""):
        self.outputSize = outputSize
        self.inputSize = inputSize
        self.name = name
        if (len(fileName) == 0):
            self.model = self.CreateModel()
            self.targetModel = self.CreateModel()
        else:
            self.model = NN.LoadNetwork(fileName)
            self.targetModel = NN.LoadNetwork(fileName)
        if train == False:
            epsilon = -1
        self.train = train
        self.fileName = fileName
        self.reward = Replay(maxLen)
        self.batch_size = batch_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilonDecay = epsilonDecay
        self.epsilonMin = epsilonMin
        self.updateFreq = updateFreq
        self.step = 0
        self.saveStep = 0
        self.saveFreq = saveFreq
        self.saveName  =saveName
        if(train==False):
            self.epsilon = self.epsilonMin
            self.batch_size = -1

    def CreateModel(self):
        model = NN.NeuralNetwork(self.inputSize, self.name)
        # model.AddLayer(126, "relu")
        model.AddLayer(16, "relu")
        model.AddLayer(self.outputSize, "softmax")
        return model

    def Train(self):
        if self.train == False or self.reward.Size() < self.batch_size:
            return
        batch = self.reward.Sample(self.batch_size)
        st = []
        tr = []
        for state, action, reward, next, done in batch:
            target = self.model.Forward(state)[0]
            rew = 0
            if done:
                rew = reward
            else:
                rew = reward + self.gamma * np.amax(
                    self.model.Forward(next)[0])
            np.put(target, action, rew + target[action])
            target = NN.Softmax(target)
            st.append(state)
            tr.append(target)
        self.model.Train(inputs=np.array(st), targets=np.array(tr), epoches=100, plotTr=False, decay=0.1, initLearningRate=0.01)
       
        self.step+=1
        if self.step % self.updateFreq == 0:
            self.UpdateTarget()
        if self.epsilon > self.epsilonMin:
            self.epsilon *= self.epsilonDecay
        return

    def Predict(self, state):
        return self.model.Forward(state)[0]

    def UpdateTarget(self):
        print("update")
        weight = self.model.GetLayers()
        self.targetModel.SetLayers(weight)
        self.targetModel.Save(self.saveName)

    def Remember(self, state, action, reward, next_state, done):
        self.reward.Add(state, action, reward, next_state, done)

    def ChooseAction(self, state):
        a = 0
        if np.random.rand() <= self.epsilon or self.reward.Size(
        ) < self.batch_size:
            a = np.random.choice(self.outputSize)
        else:
            q_values = self.Predict(state)
            a = np.argmax(q_values)
            print(a, q_values)
        return a