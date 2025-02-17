import torch
import torch.nn as nn
import torch.nn.functional as F


class BiLSTM(nn.Module):
    def __init__(self, vocab_size, embedding_size, hidden_size, dropout, pretrained_wordvector=None):
        super(BiLSTM, self).__init__()
        self.drop = nn.Dropout(dropout)
        if pretrained_wordvector is None:
            self.encoder = nn.Embedding(vocab_size, embedding_size)
        else:
            self.encoder = nn.Embedding.from_pretrained(pretrained_wordvector)
            self.encoder.requires_grad_(True)
            embedding_size = pretrained_wordvector.size(1)
        self.rnn = nn.LSTM(embedding_size, hidden_size, batch_first=True, bidirectional=True)
        self.decoder = nn.Linear(hidden_size * 2, 2)
        self.init_weights()

    def init_weights(self):
        init_range = 0.1
        self.encoder.weight.data.uniform_(-init_range, init_range)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-init_range, init_range)

    def forward(self, x):
        emb = self.drop(self.encoder(x))  # (B, L) -> (B, L, D)
        _, (hn, _) = self.rnn(emb)
        hn = self.drop(hn)

        hn = torch.cat(torch.unbind(hn, dim=0), dim=1)
        decoded = self.decoder(hn)

        out = F.log_softmax(decoded, dim=-1)
        return out
