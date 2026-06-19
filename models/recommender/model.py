# models/recommender/model.py
import torch
import torch.nn as nn

class MenuRecommender(nn.Module):
    """
    輸入：
      ingredient_ids  — 食材 token 序列  [B, max_ing]
      profile_vec     — 使用者偏好向量   [B, profile_dim]
    輸出：
      logits          — 每道料理的分數   [B, num_recipes]
    """
    def __init__(self,
                 vocab_size:   int = 200,   # 食材種類數預設，沒給就用200，實際會根據資料集調整
                 embed_dim:    int = 64,
                 num_heads:    int = 4,
                 num_layers:   int = 3,
                 profile_dim:  int = 15,    # 使用者偏好向量維度
                 num_recipes:  int = 500,
                 dropout:      float = 0.1):
        super().__init__()

        # 食材 Embedding，轉向量
        self.ingredient_emb = nn.Embedding(vocab_size , embed_dim,
                                            padding_idx=0)

        # Transformer encoder，原型食材間的關聯
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout, batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer,
                                                  num_layers=num_layers)

        # Fully Connected Layer（全連接層），特徵轉換
        self.profile_proj = nn.Linear(profile_dim, embed_dim)

        # 最終分類、Activation Function（激活函數ReLU）、避免Overfitting （拋棄）
        self.head = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim, num_recipes),
        )

    def forward(self,
                ingredient_ids: torch.Tensor,
                profile_vec:    torch.Tensor) -> torch.Tensor:

        # 食材序列 → Transformer → mean pooling
        x = self.ingredient_emb(ingredient_ids)       # [B, seq, D]
        x = self.transformer(x)                        # [B, seq, D]
        x = x.mean(dim=1)                              # [B, D]

        # 使用者偏好
        p = torch.relu(self.profile_proj(profile_vec)) # [B, D]

        # 拼接後過分類頭
        out = self.head(torch.cat([x, p], dim=1))      # [B, num_recipes]
        return out