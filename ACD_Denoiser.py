# coding: utf-8
import torch.nn as nn
import torch
import math
from torch import Tensor

from helpers import freeze_params, subsequent_mask
from transformer_layers import PositionalEncoding, TransformerDecoderLayer

class SinusoidalPositionEmbeddings(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, time):
        device = time.device
        half_dim = self.dim // 2
        embeddings = math.log(10000) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=device) * -embeddings)
        embeddings = time[:, None] * embeddings[None, :]
        embeddings = torch.cat((embeddings.sin(), embeddings.cos()), dim=-1)
        return embeddings

class ACD_Denoiser(nn.Module):

    def __init__(self,
                 num_layers: int = 2,
                 num_heads: int = 4,
                 hidden_size: int = 512,
                 ff_size: int = 2048,
                 dropout: float = 0.1,
                 emb_dropout: float = 0.1,
                 vocab_size: int = 1,
                 freeze: bool = False,
                 trg_size: int = 150,
                 decoder_trg_trg_: bool = True,
                 **kwargs):
        super(ACD_Denoiser, self).__init__()

        self.in_feature_size = trg_size + (trg_size // 3) * 4
        self.out_feature_size = trg_size

        self.pos_drop = nn.Dropout(p=emb_dropout)
        self.trg_embed = nn.Linear(self.in_feature_size, hidden_size)
        self.pe = PositionalEncoding(hidden_size, mask_count=True)
        self.emb_dropout = nn.Dropout(p=emb_dropout)

        if num_layers == 2:

            self.layers_pose_condition = TransformerDecoderLayer(
                size=hidden_size, ff_size=ff_size, num_heads=num_heads,
                dropout=dropout, decoder_trg_trg=decoder_trg_trg_)

            self.layer_norm_mid = nn.LayerNorm(hidden_size, eps=1e-6)
            self.output_layer_mid = nn.Linear(hidden_size, self.in_feature_size, bias=False)
            self.o1_embed = nn.Linear(trg_size, hidden_size)
            self.o2_embed = nn.Linear((trg_size // 3) * 4, hidden_size)

            self.layers_mha_ac = TransformerDecoderLayer(
                size=hidden_size, ff_size=ff_size, num_heads=num_heads,
                dropout=dropout, decoder_trg_trg=decoder_trg_trg_)

        self.layer_norm = nn.LayerNorm(hidden_size, eps=1e-6)

        self.time_mlp = nn.Sequential(
            SinusoidalPositionEmbeddings(hidden_size),
            nn.Linear(hidden_size, hidden_size * 2),
            nn.GELU(),
            nn.Linear(hidden_size * 2, hidden_size),
        )

        # Output layer to be the size of joints vector + 1 for counter (total is trg_size)
        self.output_layer = nn.Linear(hidden_size, trg_size, bias=False)

        if freeze:
            freeze_params(self)

    def forward(self,
                t,
                trg_embed: Tensor = None,
                encoder_output: Tensor = None,
                src_mask: Tensor = None,
                trg_mask: Tensor = None,
                **kwargs):

        assert trg_mask is not None, "trg_mask required for Transformer"
        time_embed = self.time_mlp(t)[:, None, :].repeat(1, encoder_output.shape[1], 1)
        condition = encoder_output + time_embed
        condition = self.pos_drop(condition)

        trg_embed = self.trg_embed(trg_embed)
        # add position encoding to word embedding
        x = self.pe(trg_embed)
        # Dropout if given
        x = self.emb_dropout(x)

        padding_mask = trg_mask
        # Create subsequent mask for decoding
        sub_mask = subsequent_mask(
            trg_embed.size(1)).type_as(trg_mask)

        x, h = self.layers_pose_condition(x=x, memory=condition,
                             src_mask=src_mask, trg_mask=sub_mask, padding_mask=padding_mask)

        x = self.layer_norm_mid(x)
        x = self.output_layer_mid(x)
        o_reshaped = x.view(x.shape[0], x.shape[1], 50, 7)
        o_1, o_2 = torch.split(o_reshaped, [3, 4], dim=-1)
        o_1 = o_1.reshape(o_1.shape[0], o_1.shape[1], 50 * 3)
        o_2 = o_2.reshape(o_2.shape[0], o_2.shape[1], 50 * 4)
        o_1 = self.o1_embed(o_1)
        o_2 = self.o2_embed(o_2)

        x, h = self.layers_mha_ac(x=o_1, memory=o_2,
                     src_mask=sub_mask, trg_mask=sub_mask, padding_mask=padding_mask)

        # Apply a layer normalisation
        x = self.layer_norm(x)
        # Output layer turns it back into vectors of size trg_size
        output = self.output_layer(x)

        return output

    def __repr__(self):
        return "%s(num_layers=%r, num_heads=%r)" % (
            self.__class__.__name__, len(self.layers),
            self.layers[0].trg_trg_att.num_heads)
