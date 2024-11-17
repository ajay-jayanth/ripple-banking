import torch
from torch import nn, optim


class RiskScoreModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(RiskScoreModel, self).__init__()
        self.fn1 = nn.Linear(input_size, 100)
        self.relu = nn.ReLu()
        

    def _init_weights(self):
