// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract ZNHStaking is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable znhToken;

    struct StakeInfo {
        uint256 amount;
        uint256 rewardDebt;
        uint256 lockEnd;
        uint8 lockTier; // 0=flex, 1=30d, 2=90d, 3=180d, 4=365d
    }

    // Lock tiers: duration in seconds, multiplier in basis points (10000 = 1x)
    uint256[5] public lockDurations = [0, 30 days, 90 days, 180 days, 365 days];
    uint256[5] public lockMultipliers = [10000, 12500, 15000, 20000, 30000];

    mapping(address => StakeInfo) public stakes;
    uint256 public totalStaked;
    uint256 public totalWeightedStake;
    uint256 public rewardPerShare; // scaled by 1e18
    uint256 public rewardRate; // tokens per second
    uint256 public lastRewardTime;
    uint256 public rewardPool;

    uint256 public minStake = 100 * 1e18; // 100 ZNH minimum

    event Staked(address indexed user, uint256 amount, uint8 lockTier);
    event Unstaked(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 reward);
    event RewardPoolFunded(uint256 amount);
    event MinStakeUpdated(uint256 oldMin, uint256 newMin);

    constructor(address _znhToken) Ownable(msg.sender) {
        require(_znhToken != address(0), "Zero address");
        znhToken = IERC20(_znhToken);
        lastRewardTime = block.timestamp;
        rewardRate = 0; // set by owner after funding
    }

    function _updateRewards() internal {
        if (totalWeightedStake == 0) {
            lastRewardTime = block.timestamp;
            return;
        }

        uint256 elapsed = block.timestamp - lastRewardTime;
        uint256 reward = elapsed * rewardRate;
        if (reward > rewardPool) {
            reward = rewardPool;
        }

        rewardPerShare += (reward * 1e18) / totalWeightedStake;
        rewardPool -= reward;
        lastRewardTime = block.timestamp;
    }

    function _weightedAmount(uint256 _amount, uint8 _tier) internal view returns (uint256) {
        return (_amount * lockMultipliers[_tier]) / 10000;
    }

    function stake(uint256 _amount, uint8 _lockTier) external nonReentrant {
        require(_lockTier < 5, "Invalid tier");
        require(_amount >= minStake, "Below minimum");

        StakeInfo storage info = stakes[msg.sender];
        require(info.amount == 0, "Already staking, unstake first");

        _updateRewards();

        znhToken.safeTransferFrom(msg.sender, address(this), _amount);

        uint256 weighted = _weightedAmount(_amount, _lockTier);

        info.amount = _amount;
        info.lockTier = _lockTier;
        info.lockEnd = block.timestamp + lockDurations[_lockTier];
        info.rewardDebt = (weighted * rewardPerShare) / 1e18;

        totalStaked += _amount;
        totalWeightedStake += weighted;

        emit Staked(msg.sender, _amount, _lockTier);
    }

    function unstake() external nonReentrant {
        StakeInfo storage info = stakes[msg.sender];
        require(info.amount > 0, "Nothing staked");
        require(block.timestamp >= info.lockEnd, "Still locked");

        _updateRewards();

        uint256 weighted = _weightedAmount(info.amount, info.lockTier);
        uint256 pending = (weighted * rewardPerShare) / 1e18 - info.rewardDebt;
        uint256 amount = info.amount;

        totalStaked -= amount;
        totalWeightedStake -= weighted;

        delete stakes[msg.sender];

        znhToken.safeTransfer(msg.sender, amount);
        if (pending > 0) {
            znhToken.safeTransfer(msg.sender, pending);
            emit RewardClaimed(msg.sender, pending);
        }

        emit Unstaked(msg.sender, amount);
    }

    function claimRewards() external nonReentrant {
        StakeInfo storage info = stakes[msg.sender];
        require(info.amount > 0, "Nothing staked");

        _updateRewards();

        uint256 weighted = _weightedAmount(info.amount, info.lockTier);
        uint256 pending = (weighted * rewardPerShare) / 1e18 - info.rewardDebt;
        require(pending > 0, "No rewards");

        info.rewardDebt = (weighted * rewardPerShare) / 1e18;

        znhToken.safeTransfer(msg.sender, pending);

        emit RewardClaimed(msg.sender, pending);
    }

    function pendingReward(address _user) external view returns (uint256) {
        StakeInfo storage info = stakes[_user];
        if (info.amount == 0) return 0;

        uint256 _rewardPerShare = rewardPerShare;
        if (totalWeightedStake > 0) {
            uint256 elapsed = block.timestamp - lastRewardTime;
            uint256 reward = elapsed * rewardRate;
            if (reward > rewardPool) reward = rewardPool;
            _rewardPerShare += (reward * 1e18) / totalWeightedStake;
        }

        uint256 weighted = _weightedAmount(info.amount, info.lockTier);
        return (weighted * _rewardPerShare) / 1e18 - info.rewardDebt;
    }

    function fundRewardPool(uint256 _amount) external onlyOwner {
        znhToken.safeTransferFrom(msg.sender, address(this), _amount);
        rewardPool += _amount;
        emit RewardPoolFunded(_amount);
    }

    function setRewardRate(uint256 _rate) external onlyOwner {
        _updateRewards();
        rewardRate = _rate;
    }

    function setMinStake(uint256 _minStake) external onlyOwner {
        emit MinStakeUpdated(minStake, _minStake);
        minStake = _minStake;
    }

    function getStakeInfo(address _user) external view returns (
        uint256 amount,
        uint256 lockEnd,
        uint8 lockTier,
        uint256 pending
    ) {
        StakeInfo storage info = stakes[_user];
        uint256 _pending = 0;
        if (info.amount > 0) {
            uint256 _rewardPerShare = rewardPerShare;
            if (totalWeightedStake > 0) {
                uint256 elapsed = block.timestamp - lastRewardTime;
                uint256 reward = elapsed * rewardRate;
                if (reward > rewardPool) reward = rewardPool;
                _rewardPerShare += (reward * 1e18) / totalWeightedStake;
            }
            uint256 weighted = _weightedAmount(info.amount, info.lockTier);
            _pending = (weighted * _rewardPerShare) / 1e18 - info.rewardDebt;
        }
        return (info.amount, info.lockEnd, info.lockTier, _pending);
    }
}
