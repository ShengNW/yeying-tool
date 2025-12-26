require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    // 本地开发网络
    localhost: {
      url: process.env.LOCAL_RPC_URL || "http://127.0.0.1:8545",
      chainId: parseInt(process.env.LOCAL_CHAIN_ID || "32323"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      gas: 2100000,
      gasPrice: 8000000000, // 8 Gwei
      timeout: 60000
    },
    // sepolia 测试网路
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      chainId: parseInt(process.env.SEPOLIA_CHAIN_ID || "11155111"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      gas: 2100000,
      gasPrice: 20000000000, // 20 Gwei
      timeout: 60000
    },
    // yeying 网络
    yeying: {
      url: process.env.YEYING_RPC_URL || "https://blockchain.yeying.pub",
      chainId: parseInt(process.env.YEYING_CHAIN_ID || "5432"),
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      gas: 2100000,
      gasPrice: 20000000000, // 20 Gwei
      timeout: 60000
    }
  },
  // Gas 报告
  gasReporter: {
    enabled: process.env.DEVNET_REPORT_GAS !== undefined,
    currency: "USD"
  },
  paths: {
    sources: "./contracts",
    tests: "./tests",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};
