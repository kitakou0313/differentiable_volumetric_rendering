
import torch.nn as nn
import torch.nn.functional as F
import torch
import numpy as np
from im2mesh.layers import ResnetBlockFC
import math

device = torch.device("cuda")

def mapInputCordToFourier(x):
    """
    Fourier特徴に変換
    3次元to6次元
    """
    xProj = (2.*torch.tensor(math.pi)*x).to(device)
    return torch.cat([torch.sin(xProj), torch.cos(xProj)], axis=-1).to(device)

MAPPED_INPUT_SIZE = 3*2

class Decoder(nn.Module):
    ''' Decoder class.

    As discussed in the paper, we implement the OccupancyNetwork
    f and TextureField t in a single network. It consists of 5
    fully-connected ResNet blocks with ReLU activation.

    Args:
        dim (int): input dimension
        z_dim (int): dimension of latent code z
        c_dim (int): dimension of latent conditioned code c
        hidden_size (int): hidden size of Decoder network
        leaky (bool): whether to use leaky ReLUs
        n_blocks (int): number of ResNet blocks
        out_dim (int): output dimension (e.g. 1 for only
            occupancy prediction or 4 for occupancy and
            RGB prediction)
    '''

    def __init__(self, dim=3, c_dim=128,
                 hidden_size=512, leaky=False, n_blocks=5, out_dim=4):
        super().__init__()
        self.c_dim = c_dim
        self.n_blocks = n_blocks
        self.out_dim = out_dim

        # Submodules
        self.fc_p = nn.Linear(dim*2, hidden_size)
        self.fc_out = nn.Linear(hidden_size, out_dim)

        if c_dim != 0:
            self.fc_c = nn.ModuleList([
                nn.Linear(c_dim, hidden_size) for i in range(n_blocks)
            ])

        self.blocks = nn.ModuleList([
            ResnetBlockFC(hidden_size) for i in range(n_blocks)
        ])

        if not leaky:
            self.actvn = F.relu
        else:
            self.actvn = lambda x: F.leaky_relu(x, 0.2)

    def forward(self, p, c=None, batchwise=True, only_occupancy=False,
                only_texture=False, **kwargs):

        assert((len(p.shape) == 3) or (len(p.shape) == 2))

        pMapped = mapInputCordToFourier(p)
        net = self.fc_p(pMapped)
        for n in range(self.n_blocks):
            if self.c_dim != 0 and c is not None:
                net_c = self.fc_c[n](c)
                if batchwise:
                    net_c = net_c.unsqueeze(1)
                net = net + net_c

            net = self.blocks[n](net)

        out = self.fc_out(self.actvn(net))

        if only_occupancy:
            if len(p.shape) == 3:
                out = out[:, :, 0]
            elif len(p.shape) == 2:
                out = out[:, 0]
        elif only_texture:
            if len(p.shape) == 3:
                out = out[:, :, 1:4]
            elif len(p.shape) == 2:
                out = out[:, 1:4]

        out = out.squeeze(-1)
        return out
