const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-toolbox/network-helpers");

describe("Erc20Token Contract", function () {
  // 部署合约的 fixture
  async function deployTokenFixture() {
    const [owner, addr1, addr2] = await ethers.getSigners();
    
    const Erc20Token = await ethers.getContractFactory("Erc20Token");
    const token = await Erc20Token.deploy(owner.address);
    await token.waitForDeployment();
    
    return { token, owner, addr1, addr2 };
  }
  
  describe("Deployment", function () {
    it("Should deploy successfully", async function () {
      const { token } = await loadFixture(deployTokenFixture);
      expect(await token.getAddress()).to.be.properAddress;
    });
    
    it("Should set the right owner", async function () {
      const { token, owner } = await loadFixture(deployTokenFixture);
      expect(await token.owner()).to.equal(owner.address);
    });
    
    it("Should have correct name and symbol", async function () {
      const { token } = await loadFixture(deployTokenFixture);
      expect(await token.name()).to.equal("Erc20 Token");
      expect(await token.symbol()).to.equal("TEST");
    });
  });
  
  describe("Minting", function () {
    it("Should mint tokens", async function () {
      const { token, owner, addr1 } = await loadFixture(deployTokenFixture);
      
      const mintAmount = ethers.parseEther("1000");
      await token.mint(addr1.address, mintAmount);
      
      expect(await token.balanceOf(addr1.address)).to.equal(mintAmount);
    });
  });
  
  describe("Transfers", function () {
    it("Should transfer tokens between accounts", async function () {
      const { token, owner, addr1 } = await loadFixture(deployTokenFixture);
      
      const transferAmount = ethers.parseEther("100");
      await token.transfer(addr1.address, transferAmount);
      
      expect(await token.balanceOf(addr1.address)).to.equal(transferAmount);
    });
  });
});

