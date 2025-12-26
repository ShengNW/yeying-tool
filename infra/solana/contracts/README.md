

# 安装 solana 命令行工具

```shell
# macos
brew install solana
```

# 新建一个钱包账户

```shell
# 设置为开发网络, 还有testnet、mainnet-beta
solana config set --url devnet

# 上面的设置可能无效，使用alchemy，配置url
solana config set --url https://solana-devnet.g.alchemy.com/v2/<YOUR KEY>

# 创建钱包
solana-keygen new --outfile ~/.config/solana/id.json

# 从助记词恢复钱包
solana-keygen recover 'prompt://?key=0/0' --outfile ~/.config/solana/id.json
# 系统会提示你输入助记词，输入后按回车

# 查看公钥地址
solana address

# 查看余额
solana balance

# 通过[官方水龙头](https://faucet.solana.com/)，领取测试币

```
