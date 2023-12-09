from turtle import forward
import torch

class LSTM(torch.nn.Module):
    def __init__(self,input_size, hidden_size, num_layer, output_size):
        super(LSTM, self).__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layer)
        self.linear = torch.nn.Linear(hidden_size,output_size)

    def forward(self,x):
        x,_ = self.lstm(x)
        s,b,h = x.size()
        x = x.view(s*b,h)
        x = self.linear(x)
        x = x.view(s,b,-1)
        return x