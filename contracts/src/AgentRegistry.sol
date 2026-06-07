// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract AgentRegistry is Ownable, ReentrancyGuard {
    struct Agent {
        uint256 id;
        address owner;
        string name;
        string description;
        string[] skillIds;
        bool active;
        uint256 createdAt;
        uint256 updatedAt;
    }

    uint256 private _nextAgentId = 1;
    mapping(uint256 => Agent) public agents;
    mapping(address => uint256[]) public ownerAgents;
    uint256 public totalAgents;
    uint256 public registrationFee;

    event AgentRegistered(uint256 indexed id, address indexed owner, string name);
    event AgentUpdated(uint256 indexed id, string name);
    event AgentDeactivated(uint256 indexed id);
    event AgentReactivated(uint256 indexed id);
    event RegistrationFeeUpdated(uint256 oldFee, uint256 newFee);

    constructor() Ownable(msg.sender) {
        registrationFee = 0; // free on testnet
    }

    function registerAgent(
        string calldata _name,
        string calldata _description,
        string[] memory _skillIds
    ) external payable nonReentrant returns (uint256) {
        require(bytes(_name).length > 0 && bytes(_name).length <= 64, "Invalid name");
        require(bytes(_description).length <= 512, "Description too long");
        require(_skillIds.length <= 20, "Too many skills");
        require(msg.value >= registrationFee, "Insufficient fee");

        uint256 agentId = _nextAgentId++;
        Agent storage agent = agents[agentId];
        agent.id = agentId;
        agent.owner = msg.sender;
        agent.name = _name;
        agent.description = _description;
        agent.skillIds = _skillIds;
        agent.active = true;
        agent.createdAt = block.timestamp;
        agent.updatedAt = block.timestamp;

        ownerAgents[msg.sender].push(agentId);
        totalAgents++;

        emit AgentRegistered(agentId, msg.sender, _name);

        if (msg.value > registrationFee) {
            (bool ok, ) = msg.sender.call{value: msg.value - registrationFee}("");
            require(ok, "Refund failed");
        }

        return agentId;
    }

    function updateAgent(
        uint256 _agentId,
        string calldata _name,
        string calldata _description,
        string[] memory _skillIds
    ) external {
        Agent storage agent = agents[_agentId];
        require(agent.owner == msg.sender, "Not owner");
        require(agent.active, "Agent inactive");
        require(bytes(_name).length > 0 && bytes(_name).length <= 64, "Invalid name");
        require(bytes(_description).length <= 512, "Description too long");
        require(_skillIds.length <= 20, "Too many skills");

        agent.name = _name;
        agent.description = _description;
        agent.skillIds = _skillIds;
        agent.updatedAt = block.timestamp;

        emit AgentUpdated(_agentId, _name);
    }

    function deactivateAgent(uint256 _agentId) external {
        Agent storage agent = agents[_agentId];
        require(agent.owner == msg.sender || msg.sender == owner(), "Not authorized");
        require(agent.active, "Already inactive");

        agent.active = false;
        agent.updatedAt = block.timestamp;
        totalAgents--;

        emit AgentDeactivated(_agentId);
    }

    function reactivateAgent(uint256 _agentId) external {
        Agent storage agent = agents[_agentId];
        require(agent.owner == msg.sender, "Not owner");
        require(!agent.active, "Already active");

        agent.active = true;
        agent.updatedAt = block.timestamp;
        totalAgents++;

        emit AgentReactivated(_agentId);
    }

    function getAgent(uint256 _agentId) external view returns (
        uint256 id,
        address agentOwner,
        string memory name,
        string memory description,
        string[] memory skillIds,
        bool active,
        uint256 createdAt,
        uint256 updatedAt
    ) {
        Agent storage agent = agents[_agentId];
        require(agent.createdAt > 0, "Agent not found");
        return (
            agent.id,
            agent.owner,
            agent.name,
            agent.description,
            agent.skillIds,
            agent.active,
            agent.createdAt,
            agent.updatedAt
        );
    }

    function getOwnerAgents(address _owner) external view returns (uint256[] memory) {
        return ownerAgents[_owner];
    }

    function setRegistrationFee(uint256 _fee) external onlyOwner {
        emit RegistrationFeeUpdated(registrationFee, _fee);
        registrationFee = _fee;
    }

    function withdrawFees() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No fees");
        (bool ok, ) = owner().call{value: balance}("");
        require(ok, "Withdraw failed");
    }
}
