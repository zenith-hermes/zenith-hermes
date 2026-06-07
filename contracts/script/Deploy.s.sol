// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/ZNHToken.sol";
import "../src/AgentRegistry.sol";
import "../src/SkillRegistry.sol";
import "../src/ZNHStaking.sol";

contract DeployAll is Script {
    function run() external {
        uint256 deployerKey = vm.envUint("DEPLOYER_PRIVATE_KEY");
        address deployer = vm.addr(deployerKey);

        vm.startBroadcast(deployerKey);

        // Deploy ZNH Token — all allocations to deployer for testnet
        ZNHToken token = new ZNHToken(
            deployer, // community 40%
            deployer, // ecosystem 25%
            deployer, // team 15%
            deployer, // treasury 10%
            deployer  // liquidity 10%
        );
        console.log("ZNHToken:", address(token));

        // Deploy Agent Registry
        AgentRegistry agentRegistry = new AgentRegistry();
        console.log("AgentRegistry:", address(agentRegistry));

        // Deploy Skill Registry
        SkillRegistry skillRegistry = new SkillRegistry();
        console.log("SkillRegistry:", address(skillRegistry));

        // Deploy Staking
        ZNHStaking staking = new ZNHStaking(address(token));
        console.log("ZNHStaking:", address(staking));

        // Link staking to token
        token.setStakingContract(address(staking));

        vm.stopBroadcast();

        // Write deployed addresses to file
        string memory output = string.concat(
            '{"znhToken":"', vm.toString(address(token)),
            '","agentRegistry":"', vm.toString(address(agentRegistry)),
            '","skillRegistry":"', vm.toString(address(skillRegistry)),
            '","znhStaking":"', vm.toString(address(staking)),
            '","deployer":"', vm.toString(deployer),
            '","chainId":', vm.toString(block.chainid),
            "}"
        );
        vm.writeFile("deployments.json", output);
    }
}
