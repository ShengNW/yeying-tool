
# Solana (SPL Token)

```shell
所有代币共享一个标准程序（Token Program）
每个用户的代币余额 = 独立的账户
```

# 安装 SPL Token CLI

```shell
cargo install spl-token-cli
```

# 创建新代币（创建 Mint Account）

```shell
spl-token create-token
# Creating token 7VKLZaSSX1moYDkhWAP2YfXLoyfVrS4V1DPPx5PJ7izi under program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA
```

# 创建铸币账户

```shell
spl-token create-account <token address>

# Creating account BaSVU1xpPyo5KzdRf9PSmZgDMdxFcfiyCtzrdQjxYVkn
```

# 铸造代币

```shell
spl-token mint <token address> 1000000

# Minting 1000000 tokens
#   Token: 7VKLZaSSX1moYDkhWAP2YfXLoyfVrS4V1DPPx5PJ7izi
#   Recipient: BaSVU1xpPyo5KzdRf9PSmZgDMdxFcfiyCtzrdQjxYVkn
```

# 转移代币

```shell
# --allow-unfunded-recipient 允许接收者地址还没有创建对应的代币账户
# --fund-recipient 从你的钱包支付租金

spl-token transfer <token address> 100 <接收者地址> --allow-unfunded-recipient --fund-recipient

# Transfer 100 tokens
#   Sender: BaSVU1xpPyo5KzdRf9PSmZgDMdxFcfiyCtzrdQjxYVkn
#   Recipient: FF4GJPmbGRUWKSPV1YB8BdRj63t25ahuFGtXqZXeGEWc
#   Recipient associated token account: 7P3st3CSvhJcECdGDXZFACv2iEsvbNYPLy7Vxc76iTrK
#   Funding recipient: 7P3st3CSvhJcECdGDXZFACv2iEsvbNYPLy7Vxc76iTrK

Signature: 3YTvaDZDzWYhrxcEDh85vheMmpvwJAfb1cnFeSC37E5vV3MrgbqPLHEiJd488bk7Lpk1Rjauot3ZSGFzuRyGaarq
```

# 查看代币信息

```shell
spl-token display <token address>
```

# 查询指定钱包地址的代币余额
```shell
spl-token balance <代币地址> --owner <钱包地址>

# 100
```

# 查看钱包的所有代币
```shell
spl-token accounts --owner <钱包地址>

# Token                                         Balance
# -----------------------------------------------------
# 7VKLZaSSX1moYDkhWAP2YfXLoyfVrS4V1DPPx5PJ7izi  100
```

