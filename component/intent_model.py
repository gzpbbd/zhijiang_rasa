import abc
import torch
from torch import nn, optim
import torch.nn.functional as F
from typing import List, Set
import os
from bert_serving.client import BertClient
import numpy as np
import pickle


class IntentModelInterface:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def train(self, texts: List[str], labels: List[str], intents: Set[str], epochs: int):
        pass

    @abc.abstractmethod
    def save(self, filepath: str):
        pass

    @abc.abstractmethod
    def load(self, filepath: str):
        pass

    @abc.abstractmethod
    def process(self, text: str):
        return


class IntentModel(IntentModelInterface):

    def __init__(self):
        self.idx2intent = None
        self.intent2idx = None
        self.net = None
        self.bert_client = BertClient()

    def train(self, texts: List[str], labels: List[str], intents: Set[str], epochs: int):
        self.idx2intent = dict((i, intent) for i, intent in enumerate(intents))
        self.intent2idx = dict((intent, i) for i, intent in enumerate(intents))

        # X
        texts_np = self.bert_client.encode(texts)
        # Y
        labels_np = np.array([self.intent2idx[label] for label in labels])
        # 洗牌
        tmp = np.random.permutation(len(texts_np))
        texts_np = texts_np[tmp]
        labels_np = labels_np[tmp]

        input_data = torch.tensor(texts_np)
        output_data = torch.tensor(labels_np)

        # 输入与输出的维度
        in_size = texts_np.shape[-1]
        out_size = len(intents)

        # 网络、损失函数、优化器
        self.net = Net(in_size, out_size)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.RMSprop(self.net.parameters(), lr=0.001)

        batch_size = 32
        for epoch in range(epochs):
            total_loss = 0
            for i in range(len(input_data) // batch_size):
                batch_x = input_data[i * batch_size:min((i + 1) * batch_size, len(input_data))]
                batch_y = output_data[i * batch_size:min((i + 1) * batch_size, len(output_data))]

                # 梯度清零
                optimizer.zero_grad()
                # 前向传播，计算损失，反向传播计算梯度，更新梯度
                batch_y_pred = self.net(batch_x)
                loss = criterion(batch_y_pred, batch_y)
                loss.backward()
                optimizer.step()

                # 打印损失
                total_loss += loss.item()
            print('loss: {:.2f}'.format(total_loss))

    def save(self, filepath: str):
        # 保存 intent 与 index 的索引
        # 保存 模型
        torch.save(self.net, filepath + '.pt')
        with open(filepath + 'idx_and_intent.pkl', 'wb') as f:
            data = {'idx2intent': self.idx2intent, 'intent2idx': self.intent2idx}
            pickle.dump(data, f)

    def load(self, filepath: str):
        self.net = torch.load(filepath + '.pt')
        with open(filepath + 'idx_and_intent.pkl', 'rb') as f:
            data = pickle.load(f)
            self.idx2intent = data['idx2intent']
            self.intent2idx = data['intent2idx']

    def process(self, text: str):
        texts_np = self.bert_client.encode([text])
        input_data = torch.tensor(texts_np)
        pred = self.net.predict(input_data)
        pred = torch.squeeze(pred, dim=0).tolist()

        result = dict()
        for i, prob in enumerate(pred):
            intent = self.idx2intent[i]
            result[intent] = prob
        return result


class Net(nn.Module):
    def __init__(self, in_size, out_size):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(in_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, out_size)

    def forward(self, x):
        # 前向传播，计算模型的输出
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def predict(self, x):
        x = self.forward(x)
        return F.softmax(x, dim=-1)
