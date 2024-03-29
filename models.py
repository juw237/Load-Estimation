# -*- coding:utf-8 -*-
"""

"""
from torch import nn
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# class LSTM(nn.Module):
#     def __init__(self, input_size, hidden_size, num_layers, output_size, batch_size):
#         super().__init__()
#         self.input_size = input_size
#         self.hidden_size = hidden_size
#         self.num_layers = num_layers
#         self.output_size = output_size
#         self.num_directions = 1
#         self.batch_size = batch_size
#         self.lstm = nn.LSTM(self.input_size, self.hidden_size, self.num_layers, batch_first=True)
#         self.linear = nn.Linear(self.hidden_size, self.output_size)
#
#     def forward(self, input_seq):
#         batch_size, seq_len = input_seq.shape[0], input_seq.shape[1]
#         h_0 = torch.randn(self.num_directions * self.num_layers, batch_size, self.hidden_size).to(device)
#         c_0 = torch.randn(self.num_directions * self.num_layers, batch_size, self.hidden_size).to(device)
#         # print(input_seq.size())
#         # input(batch_size, seq_len, input_size)
#         # output(batch_size, seq_len, num_directions * hidden_size)
#         output, _ = self.lstm(input_seq, (h_0, c_0))
#         pred = self.linear(output)  # pred(batch_size, seq_len, output_size)
#         pred = pred[:, -1, :]
#
#         return pred
#
#
# class BiLSTM(nn.Module):
#     def __init__(self, input_size, hidden_size, num_layers, output_size, batch_size):
#         super().__init__()
#         self.input_size = input_size
#         self.hidden_size = hidden_size
#         self.num_layers = num_layers
#         self.output_size = output_size
#         self.num_directions = 2
#         self.batch_size = batch_size
#         self.lstm = nn.LSTM(self.input_size, self.hidden_size, self.num_layers, batch_first=True, bidirectional=True)
#         self.linear = nn.Linear(self.num_directions * self.hidden_size, self.output_size)
#
#     def forward(self, input_seq):
#         batch_size, seq_len = input_seq.shape[0], input_seq.shape[1]
#         h_0 = torch.randn(self.num_directions * self.num_layers, batch_size, self.hidden_size).to(device)
#         c_0 = torch.randn(self.num_directions * self.num_layers, batch_size, self.hidden_size).to(device)
#         output, _ = self.lstm(input_seq, (h_0, c_0))
#         pred = self.linear(output)
#         pred = pred[:, -1, :]
#
#         return pred
#

class Encoder(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, batch_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_directions = 1
        self.batch_size = batch_size
        self.lstm = nn.LSTM(self.input_size, self.hidden_size, self.num_layers, batch_first=True, bidirectional=False, dropout = 0.3)
    def forward(self, input_seq):
        batch_size, seq_len = input_seq.shape[0], input_seq.shape[1]
        h_0 = torch.randn(self.num_directions * self.num_layers, batch_size, self.hidden_size).to(device)
        c_0 = torch.randn(self.num_directions * self.num_layers, batch_size, self.hidden_size).to(device)
        output, (h, c) = self.lstm(input_seq, (h_0, c_0))
        return h, c

class Decoder(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, batch_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.num_directions = 1
        self.batch_size = batch_size
        self.lstm = nn.LSTM(input_size, self.hidden_size, self.num_layers, batch_first=True, bidirectional=False,dropout = 0.3)
        self.linear = nn.Linear(self.hidden_size, self.input_size)

    def forward(self, input_seq, h, c):
        # input_seq(batch_size, input_size)
        input_seq = input_seq.unsqueeze(1) #Add dimension by 1 , LSTM output 2D   ——》 LSTM Input 3D
        output, (h, c) = self.lstm(input_seq, (h, c))
        # output(batch_size, seq_len, num * hidden_size)
        pred = self.linear(output.squeeze(1))  # pred(batch_size, 1, output_size)

        return pred, h, c

class Seq2Seq(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, batch_size):
        super().__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.Encoder = Encoder(input_size, hidden_size, num_layers, batch_size)
        self.Decoder = Decoder(input_size, hidden_size, num_layers, output_size, batch_size)

    def forward(self, input_seq):
        target_len = self.output_size  # 预测步长
        batch_size, seq_len, _ = input_seq.shape[0], input_seq.shape[1], input_seq.shape[2]
        h, c = self.Encoder(input_seq)
        outputs = torch.zeros(batch_size, self.input_size, self.output_size).to(device)#？？？
        decoder_input = input_seq[:, -1, :] #decoder第一个input 是 encoder 最后一个输入
        for t in range(target_len):
            decoder_output, h, c = self.Decoder(decoder_input, h, c)
            outputs[:, :, t] = decoder_output
            decoder_input = decoder_output

        return outputs[:, 0, :] #为了输入输出匹配，这里decoder_output包含了所有变量未来一个步长的预测值，最后我们只需要取第一个也就是负荷的预测值即可：
