// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract SkillRegistry is Ownable {
    struct Skill {
        uint256 id;
        address creator;
        string name;
        string category;
        string description;
        string version;
        bool verified;
        bool active;
        uint256 installs;
        uint256 createdAt;
        uint256 updatedAt;
    }

    uint256 private _nextSkillId = 1;
    mapping(uint256 => Skill) public skills;
    mapping(string => uint256) public skillByName;
    mapping(address => uint256[]) public creatorSkills;
    mapping(string => uint256[]) public categorySkills;
    uint256 public totalSkills;

    address[] public verifiers;
    mapping(address => bool) public isVerifier;

    event SkillRegistered(uint256 indexed id, address indexed creator, string name, string category);
    event SkillVerified(uint256 indexed id, address indexed verifier);
    event SkillInstalled(uint256 indexed id, address indexed user);
    event SkillUpdated(uint256 indexed id, string version);
    event SkillDeactivated(uint256 indexed id);
    event VerifierAdded(address indexed verifier);
    event VerifierRemoved(address indexed verifier);

    constructor() Ownable(msg.sender) {
        isVerifier[msg.sender] = true;
        verifiers.push(msg.sender);
    }

    modifier onlyVerifier() {
        require(isVerifier[msg.sender], "Not a verifier");
        _;
    }

    function registerSkill(
        string calldata _name,
        string calldata _category,
        string calldata _description,
        string calldata _version
    ) external returns (uint256) {
        require(bytes(_name).length > 0 && bytes(_name).length <= 64, "Invalid name");
        require(bytes(_category).length > 0, "Invalid category");
        require(bytes(_description).length <= 1024, "Description too long");
        require(skillByName[_name] == 0, "Name taken");

        uint256 skillId = _nextSkillId++;
        Skill storage skill = skills[skillId];
        skill.id = skillId;
        skill.creator = msg.sender;
        skill.name = _name;
        skill.category = _category;
        skill.description = _description;
        skill.version = _version;
        skill.active = true;
        skill.createdAt = block.timestamp;
        skill.updatedAt = block.timestamp;

        skillByName[_name] = skillId;
        creatorSkills[msg.sender].push(skillId);
        categorySkills[_category].push(skillId);
        totalSkills++;

        emit SkillRegistered(skillId, msg.sender, _name, _category);
        return skillId;
    }

    function verifySkill(uint256 _skillId) external onlyVerifier {
        Skill storage skill = skills[_skillId];
        require(skill.createdAt > 0, "Skill not found");
        require(!skill.verified, "Already verified");

        skill.verified = true;
        skill.updatedAt = block.timestamp;

        emit SkillVerified(_skillId, msg.sender);
    }

    function installSkill(uint256 _skillId) external {
        Skill storage skill = skills[_skillId];
        require(skill.active, "Skill inactive");

        skill.installs++;

        emit SkillInstalled(_skillId, msg.sender);
    }

    function updateSkill(
        uint256 _skillId,
        string calldata _description,
        string calldata _version
    ) external {
        Skill storage skill = skills[_skillId];
        require(skill.creator == msg.sender, "Not creator");
        require(skill.active, "Skill inactive");

        skill.description = _description;
        skill.version = _version;
        skill.updatedAt = block.timestamp;

        emit SkillUpdated(_skillId, _version);
    }

    function deactivateSkill(uint256 _skillId) external {
        Skill storage skill = skills[_skillId];
        require(skill.creator == msg.sender || msg.sender == owner(), "Not authorized");
        require(skill.active, "Already inactive");

        skill.active = false;
        skill.updatedAt = block.timestamp;
        totalSkills--;

        emit SkillDeactivated(_skillId);
    }

    function getSkill(uint256 _skillId) external view returns (Skill memory) {
        require(skills[_skillId].createdAt > 0, "Skill not found");
        return skills[_skillId];
    }

    function getSkillsByCategory(string calldata _category) external view returns (uint256[] memory) {
        return categorySkills[_category];
    }

    function getCreatorSkills(address _creator) external view returns (uint256[] memory) {
        return creatorSkills[_creator];
    }

    function addVerifier(address _verifier) external onlyOwner {
        require(!isVerifier[_verifier], "Already verifier");
        isVerifier[_verifier] = true;
        verifiers.push(_verifier);
        emit VerifierAdded(_verifier);
    }

    function removeVerifier(address _verifier) external onlyOwner {
        require(isVerifier[_verifier], "Not verifier");
        isVerifier[_verifier] = false;
        emit VerifierRemoved(_verifier);
    }
}
