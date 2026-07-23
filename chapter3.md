# 第三章
- 经典的Transformer架构：
```python

import torch
import torch.nn as nn
import math

# --- 占位符模块，将在后续小节中实现 ---

class PositionalEncoding(nn.Module):
    """
    位置编码模块
    """
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # 创建一个足够长的位置编码矩阵
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))

        # pe (positional encoding) 的大小为 (max_len, d_model)
        pe = torch.zeros(max_len, d_model)

        # 偶数维度使用 sin, 奇数维度使用 cos
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        # 将 pe 注册为 buffer，这样它就不会被视为模型参数，但会随模型移动（例如 to(device)）
        self.register_buffer('pe', pe.unsqueeze(0))
        
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x.size(1) 是当前输入的序列长度
        # 将位置编码加到输入向量上
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)

class MultiHeadAttention(nn.Module):
    """
    多头注意力机制模块
    """
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        assert d_model % num_heads == 0, "d_model 必须能被 num_heads 整除"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        # 定义 Q, K, V 和输出的线性变换层
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    
    
    def scaled_dot_product_attention(self, Q, K, V, mask=None):
        # 1. 计算注意力得分 (QK^T)
        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        # 2. 应用掩码 (如果提供)
        if mask is not None:
            # 将掩码中为 0 的位置设置为一个非常小的负数，这样 softmax 后会接近 0
            attn_scores = attn_scores.masked_fill(mask == 0, -1e9)

        # 3. 计算注意力权重 (Softmax)
        attn_probs = torch.softmax(attn_scores, dim=-1)

        # 4. 加权求和 (权重 * V)
        output = torch.matmul(attn_probs, V)
        return output
    
    def split_heads(self, x):
        # 将输入 x 的形状从 (batch_size, seq_length, d_model)
        # 变换为 (batch_size, num_heads, seq_length, d_k)
        batch_size, seq_length, d_model = x.size()
        return x.view(batch_size, seq_length, self.num_heads, self.d_k).transpose(1, 2)
    
    def combine_heads(self, x):
        # 将输入 x 的形状从 (batch_size, num_heads, seq_length, d_k)
        # 变回 (batch_size, seq_length, d_model)
        batch_size, num_heads, seq_length, d_k = x.size()
        return x.transpose(1, 2).contiguous().view(batch_size, seq_length, self.d_model)
    
    def forward(self, Q, K, V, mask=None):
        # 1. 对 Q, K, V 进行线性变换
        Q = self.split_heads(self.W_q(Q))
        K = self.split_heads(self.W_k(K))
        V = self.split_heads(self.W_v(V))

        # 2. 计算缩放点积注意力
        attn_output = self.scaled_dot_product_attention(Q, K, V, mask)

        # 3. 合并多头输出并进行最终的线性变换
        output = self.W_o(self.combine_heads(attn_output))
        return output

class PositionWiseFeedForward(nn.Module):
    """
    位置前馈网络模块
    """
    def __init__(self, d_model, d_ff, dropout=0.1):
        super(PositionWiseFeedForward, self).__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.relu = nn.ReLU()
        
        
    def forward(self, x):
        # x 形状: (batch_size, seq_len, d_model)
        x = self.linear1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.linear2(x)
        # 最终输出形状: (batch_size, seq_len, d_model)
        return x

# --- 编码器核心层 ---

class EncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(EncoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads) 
        self.feed_forward = PositionWiseFeedForward(d_model, d_ff, dropout) 
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask):
        # 残差连接与层归一化将在 3.1.2.4 节中详细解释
        # 1. 多头自注意力
        attn_output = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # 2. 前馈网络
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x

# --- 解码器核心层 ---

class DecoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout):
        super(DecoderLayer, self).__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads) 
        self.cross_attn = MultiHeadAttention(d_model, num_heads) 
        self.feed_forward = PositionWiseFeedForward(d_model, d_ff, dropout) 
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, encoder_output, src_mask, tgt_mask):
        # 1. 掩码多头自注意力 (对自己)
        attn_output = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_output))

        # 2. 交叉注意力 (对编码器输出)
        cross_attn_output = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout(cross_attn_output))

        # 3. 前馈网络
        ff_output = self.feed_forward(x)
        x = self.norm3(x + self.dropout(ff_output))

        return x
```

- 编码器层 EncoderLayer 完整维度流
| 步骤序号 | 操作名称 | 对应代码位置 | 张量形状 | 核心说明 |
|----------|----------|--------------|-----------|----------|
| 1 | 层输入 | `forward(x, mask)` 入参 | `(2, 10, 512)` | 经过词嵌入（Embedding）和位置编码（Positional Encoding）后的编码器输入。 |
| 2 | 多头自注意力计算 | `self.self_attn(x, x, x, mask)` | `(2, 10, 512)` | Q、K、V 均来自输入 `x`，经过多头自注意力计算后输出维度与输入保持一致。 |
| 3 | 残差连接 + Dropout | `x + self.dropout(attn_output)` | `(2, 10, 512)` | 将注意力输出与原输入逐元素相加，并进行 Dropout，张量形状保持不变。 |
| 4 | 第一层归一化 | `self.norm1(...)` | `(2, 10, 512)` | 使用 Layer Normalization 沿最后一维进行归一化，仅改变数值分布，不改变张量形状。 |
| 5 | 前馈网络 - 升维线性层 | `self.feed_forward.linear1(x)` | `(2, 10, 2048)` | 第一个全连接层，将特征维度从 `d_model=512` 升维至 `d_ff=2048`。 |
| 6 | 激活 + Dropout | `ReLU + Dropout` | `(2, 10, 2048)` | 对升维后的特征进行 ReLU 激活，并执行 Dropout，张量形状保持不变。 |
| 7 | 前馈网络 - 降维线性层 | `self.feed_forward.linear2(x)` | `(2, 10, 512)` | 第二个全连接层，将特征维度从 `d_ff=2048` 降维回 `d_model=512`。 |
| 8 | 第二次残差连接 + Dropout | `x + self.dropout(ff_output)` | `(2, 10, 512)` | 将前馈网络输出与输入逐元素相加，并进行 Dropout，张量形状保持不变。 |
| 9 | 第二层归一化 + 层输出 | `self.norm2(...)` | `(2, 10, 512)` | 对结果进行第二次 Layer Normalization，得到单层编码器最终输出，其形状与输入完全一致，可继续堆叠后续 Encoder Layer。 |

- 解码器层 DecoderLayer 完整维度流
| 步骤序号 | 操作名称 | 对应代码位置 | 张量形状 | 核心说明 |
|----------|----------|--------------|-----------|----------|
| 1 | 层输入 | `forward(x, encoder_output, src_mask, tgt_mask)` | `x: (2, 8, 512)`<br>`encoder_output: (2, 10, 512)` | `x` 为目标端词嵌入（Embedding）与位置编码（Positional Encoding）后的输入；`encoder_output` 为编码器最终输出。 |
| 2 | 掩码多头自注意力 | `self.self_attn(x, x, x, tgt_mask)` | `(2, 8, 512)` | Q、K、V 均来自解码器输入 `x`，使用因果掩码（Causal Mask），保证当前位置只能关注当前位置及之前的 Token，输出序列长度保持 `tgt_seq_len=8`。 |
| 3 | 第一次残差连接 + Dropout | `x + self.dropout(attn_output)` | `(2, 8, 512)` | 将掩码自注意力输出与输入逐元素相加，并进行 Dropout，张量形状保持不变。 |
| 4 | 第一层归一化 | `self.norm1(...)` | `(2, 8, 512)` | 使用 Layer Normalization 沿最后一维进行归一化，仅改变数值分布，不改变张量形状。 |
| 5 | 交叉注意力计算 | `self.cross_attn(x, encoder_output, encoder_output, src_mask)` | `(2, 8, 512)` | Query（Q）来自解码器输出，Key（K）和 Value（V）来自编码器输出，输出序列长度由 Query 决定，因此保持目标端长度 `8`。 |
| 6 | 第二次残差连接 + Dropout | `x + self.dropout(cross_attn_output)` | `(2, 8, 512)` | 将交叉注意力输出与输入逐元素相加，并进行 Dropout，张量形状保持不变。 |
| 7 | 第二层归一化 | `self.norm2(...)` | `(2, 8, 512)` | 使用第二次 Layer Normalization，对特征进行归一化处理，不改变张量形状。 |
| 8 | 前馈网络 - 升维线性层 | `self.feed_forward.linear1(x)` | `(2, 8, 2048)` | 前馈网络第一层全连接，将特征维度从 `d_model=512` 升维到 `d_ff=2048`。 |
| 9 | 激活 + Dropout | `ReLU + Dropout` | `(2, 8, 2048)` | 对升维后的特征进行 ReLU 激活，并执行 Dropout，张量形状保持不变。 |
| 10 | 前馈网络 - 降维线性层 | `self.feed_forward.linear2(x)` | `(2, 8, 512)` | 前馈网络第二层全连接，将特征维度从 `d_ff=2048` 降维回 `d_model=512`。 |
| 11 | 第三次残差连接 + Dropout | `x + self.dropout(ff_output)` | `(2, 8, 512)` | 将前馈网络输出与输入逐元素相加，并进行 Dropout，张量形状保持不变。 |
| 12 | 第三层归一化 + 层输出 | `self.norm3(...)` | `(2, 8, 512)` | 使用第三次 Layer Normalization，得到单层解码器最终输出，其形状与解码器输入保持一致，可继续堆叠后续 Decoder Layer。 |



