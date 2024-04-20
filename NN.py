import numpy as np
import matplotlib.pyplot as plt
import datetime
import json

def Relu(x):
    return np.maximum(0, x)
def Softmax(x):
    exps = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return exps / np.sum(exps, axis=-1, keepdims=True)
def MeanSquaredError(y_true, y_pred):
    return np.mean(np.square(y_true - y_pred))

def CrossEntropy(y_true, y_pred):
    return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))
class Layer():
    def __init__(self, inputSize, outputSize, activation):
        self.inputSize = inputSize
        self.outputSize = outputSize
        self.activation = activation
        self.weights = np.random.randn(inputSize, outputSize) * np.sqrt(2.0 / inputSize)
        self.bias = np.zeros((1, outputSize))
        self.mWeights = np.zeros((inputSize, outputSize))
        self.vWeights = np.zeros((inputSize, outputSize))
        self.mBiases = np.zeros((1, outputSize))
        self.vBiases = np.zeros((1, outputSize))
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.epsilon = 1e-8
        self.backWeight = []
        self.backBias = []

    def Forward(self, x):
        self.x = x
        z = np.dot(self.x, self.weights) + self.bias 
        if self.activation == "relu":
            self.output = Relu(z)
            
        elif self.activation == "softmax":
            
            self.output = Softmax(z)
            
        else: 
            pass
            
        return self.output 
    def Backward(self, dValues, learningRate, t):
        if self.activation == "softmax":
            for i, grad in enumerate(dValues):
                if len(grad.shape) == 1:  
                    grad = grad.reshape(-1, 1)
                jacobMatrix = np.diagflat(grad) - np.dot(grad, grad.T)
                dValues[i] = np.dot(jacobMatrix, self.output[i])
                
        elif self.activation == "relu":
            dValues = dValues * (self.output > 0)
            
        dWeights = np.dot(self.x.T, dValues)
        bBias = np.sum(dValues, axis=0, keepdims=True)
        dWeights = np.clip(dWeights, -1.0, 1.0)
        bBias = np.clip(bBias, -1.0, 1.0)
        dInput = np.dot(dValues, self.weights.T)
        self.backWeight = np.copy(self.weights)
        self.backBias = np.copy(self.bias)
        self.weights -= learningRate * dWeights
        self.bias -= learningRate * bBias 
        mWeights = self.beta1 * self.mWeights + (1 - self.beta1) * dWeights
        vWeights = self.beta2 * self.vWeights + (1 - self.beta2) * (dWeights ** 2)
        mHatWeights = mWeights / (1 - self.beta1 ** t)
        vHatWeights = vWeights / (1 - self.beta2 ** t)
        self.weights -= learningRate * mHatWeights / (np.sqrt(vHatWeights) + self.epsilon)
        mBiases = self.beta1 * self.mBiases + (1 - self.beta1) * bBias
        vBiases = self.beta2 * self.vBiases + (1 - self.beta2) * (bBias ** 2)
        mHat = mBiases / (1 - self.beta1 ** t)
        v_hat_biases = vBiases / (1 - self.beta2 ** t)
        self.bias -= learningRate * mHat / (np.sqrt(v_hat_biases) + self.epsilon)
        return dInput
    def BackOne(self):
        self.weights = np.copy(self.backWeight)
        self.bias = np.copy(self.backBias)
    def __str__(self) -> str:
        return "Layer(inputSize={}, outputSize={}, activationFunction={})".format(self.inputSize, self.outputSize, self.activation)
    def ToString(self):
        data = {
            "inputSize":self.inputSize,
            "outputSize":self.outputSize,
            "activation":self.activation,
            "weights":self.weights.tolist(),
            "bias":self.bias.tolist(),
            "mWeights":self.mWeights.tolist(),
            "vWeights":self.vWeights.tolist(),
            "mBiases":self.mBiases.tolist(),
            "vBiases":self.vBiases.tolist(),
            "beta1":self.beta1,
            "beta2":self.beta2,
            "epsilon":self.epsilon
        }
        return data
    def FromString(self, s):
        self.inputSize = s["inputSize"]
        self.outputSize = s["outputSize"]
        self.activation = s["activation"]
        self.weights = s["weights"]
        self.bias = s["bias"]
        self.mWeights = s["mWeights"]
        self.vWeights = s["vWeights"]
        self.mBiases = s["mBiases"]
        self.vBiases = s["vBiases"]
        self.beta1 = s["beta1"]
        self.beta2 = s["beta2"]
        self.epsilon = s["epsilon"]

        return ""
    def GetData(self):
        w = np.copy(self.weights)
        b = np.copy(self.bias)
        return w, b
    def SetData(self, data):
        self.weights = np.copy(data[0])
        self.bias = np.copy(data[1])
class NeuralNetwork():
    def __init__(self, inputSize, name):
        self.lastLayerSize = inputSize
        self.name = name
        self.accuracy = 0
        self.layers = []
        self.losslog = []
        self.accLog = []
    
    def AddLayer(self, size, activation="relu"):
        self.layers.append(Layer(self.lastLayerSize, size, activation))
        self.lastLayerSize = size
    def ShowLayers(self):
        for i in self.layers:
            print(i)
    def Forward(self, x):
        for layer in self.layers:
            x = layer.Forward(x)
        return x
    def ShowGraphic(self, x, y1, y2):
        fig, (ax1, ax2) = plt.subplots(1, 2)

        ax1.plot(x, y1,)
        ax1.set_title('loss')
        ax1.set_xlabel('Index')
        ax1.set_ylabel('Value')

        ax2.plot(x, y2)
        ax2.set_title('acc')
        ax2.set_xlabel('Index')
        ax2.set_ylabel('Value')

        plt.tight_layout()

        plt.show()
        

    def Train(self, inputs, targets, epoches, initLearningRate, decay,learningRateMin = 1e-10, plotTr=False):
        t = 0
        if plotTr == True:
            self.losslog = []
            self.accLog = []
        preLoss=-1
        learningRate = initLearningRate
        for epoch in range(epoches):
            output = self.Forward(inputs)
            epsilon = 1e-10
            loss = -np.mean(targets * np.log(output + epsilon))
            pLabel = np.argmax(output, axis=1)
            tLabel = np.argmax(targets, axis=1)
            accuracy = np.mean(pLabel == tLabel)*100
            oGrad = (output - targets) / output.shape[0]
            if(preLoss == -1):
                preLoss = loss
            else:
                if(loss > preLoss):
                    initLearningRate = initLearningRate * decay
                    if(initLearningRate < learningRateMin):
                        break
                    for i in self.layers:
                        i.BackOne()
                    output = self.Forward(inputs)
                    epsilon = 1e-10
                    loss = -np.mean(targets * np.log(output + epsilon))
                    pLabel = np.argmax(output, axis=1)
                    tLabel = np.argmax(targets, axis=1)
                    accuracy = np.mean(pLabel == tLabel)*100
                    oGrad = (output - targets) / output.shape[0]
                    t -= 1
                else:
                    preLoss = loss
            t += 1
            learningRate = initLearningRate / (1 + decay * epoch)
            for i in range(len(self.layers)-1, -1, -1):
                oGrad = self.layers[i].Backward(oGrad, learningRate, t)
            if plotTr == True:
                self.losslog.append(loss)
                self.accLog.append(accuracy)
                self.plotX = epoch + 1
        self.accuracy = accuracy
        if plotTr == True:
            self.ShowGraphic(range(epoches), self.losslog, self.accLog)
    def GetLayers(self):
        layer = []
        for i in self.layers:
            layer.append(i.GetData())
        return layer
    def SetLayers(self, layers):
        for i in range(len(layers)):
            self.layers[i].SetData(layers[i])
            



    def Save(self, name):
        layerData = []
        for i in self.layers:
            layerData.append(i.ToString())
        data = {
            "layers":layerData,
            "name":self.name,
            "accuracy":self.accuracy
        }
        file = open(name, "w")
        json.dump(data, file)
        file.close()
        
    def Load(self, name):
        file = open(name, "r")
        data = file.read()
        data = eval(data)
        file.close()
        for i in data["layers"]:
            layer = Layer(1, 1, "")
            layer.FromString(i)
            self.layers.append(layer)
        self.name = data["name"]
        self.accuracy = data["accuracy"]

def LoadNetwork(name):
    nn = NeuralNetwork(1, "")
    nn.Load(name)
    return nn