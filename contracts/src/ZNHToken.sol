// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract ZNHToken is ERC20, ERC20Burnable, ERC20Permit, Ownable {
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 1e18; // 1B tokens

    // Allocation percentages (basis points, 10000 = 100%)
    uint16 public constant COMMUNITY_BPS = 4000;   // 40%
    uint16 public constant ECOSYSTEM_BPS = 2500;    // 25%
    uint16 public constant TEAM_BPS = 1500;         // 15%
    uint16 public constant TREASURY_BPS = 1000;     // 10%
    uint16 public constant LIQUIDITY_BPS = 1000;    // 10%

    address public stakingContract;

    event StakingContractUpdated(address indexed oldAddr, address indexed newAddr);

    constructor(
        address _community,
        address _ecosystem,
        address _team,
        address _treasury,
        address _liquidity
    ) ERC20("Zenith Hermes", "ZNH") ERC20Permit("Zenith Hermes") Ownable(msg.sender) {
        require(
            _community != address(0) &&
            _ecosystem != address(0) &&
            _team != address(0) &&
            _treasury != address(0) &&
            _liquidity != address(0),
            "Zero address"
        );

        _mint(_community, (MAX_SUPPLY * COMMUNITY_BPS) / 10000);
        _mint(_ecosystem, (MAX_SUPPLY * ECOSYSTEM_BPS) / 10000);
        _mint(_team, (MAX_SUPPLY * TEAM_BPS) / 10000);
        _mint(_treasury, (MAX_SUPPLY * TREASURY_BPS) / 10000);
        _mint(_liquidity, (MAX_SUPPLY * LIQUIDITY_BPS) / 10000);
    }

    function setStakingContract(address _staking) external onlyOwner {
        emit StakingContractUpdated(stakingContract, _staking);
        stakingContract = _staking;
    }
}
