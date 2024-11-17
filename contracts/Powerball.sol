// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Powerball{
    uint256 public ticketPrice = 1e17;
    address public owner;
    
    uint256 constant MAX_NUMBER = 69;
    uint256 constant MAX_POWERBALL_NUMBER = 26;
    uint256 constant GAME_LENGTH = 3 days;
    struct Round{
        uint256 endTime;
        uint256 drawBlock;
        uint256[6] winningNumbers;
        mapping (address => uint256[6][]) tickets;
    }
    mapping (uint => Round) public rounds;
    uint256 public round;
    constructor(){
        owner = msg.sender;
        round = 1;
        rounds[round].endTime = block.timestamp + GAME_LENGTH;
    }
    // for receiving ether to the smart contract
    // for solidity version < 0.6.1 user function () public payable {}
    receive() external payable {

    }
    function buy(uint[6][] memory ticket) public payable returns (uint256) {
        require(ticket.length * ticketPrice <= msg.value,"Insufficient amount for tickets");
        for(uint i = 0; i < ticket.length; i++){
            for(uint j = 0; j < 5; j++){
                require(ticket[i][j] <= MAX_NUMBER,"A number is not less than 69");
                require(ticket[i][j] > 0, "A number is not greater than 0");
            }
            require(ticket[i][5] <= MAX_POWERBALL_NUMBER,"All powerball number should be less than 27");
            require(ticket[i][5] > 0,"All powerball numbers should be greater than 0 ");
        }

        // Check whether current round entry has expired
        if(block.timestamp > rounds[round].endTime){
            rounds[round].drawBlock = block.number + 3;
            round += 1;
            rounds[round].endTime = block.timestamp + GAME_LENGTH;
        }
        for (uint i  = 0; i < ticket.length; i++){
            rounds[round].tickets[msg.sender].push(ticket[i]);
        }
        return round;
    }
    function drawNumber(uint256 _round) public{
        Round storage drawRound = rounds[_round];
        require(drawRound.endTime < block.timestamp, "Time to draw number for this round has not been reached");
        require(drawRound.drawBlock > block.number,"Block number for drawing round has not been reached");
        require(drawRound.winningNumbers[0] == 0,"Winning numbers for this round has been chosen");

        for(uint i = 0; i < 5; i++){
            bytes32 randomNumber = keccak256(abi.encodePacked(blockhash(drawRound.drawBlock),i));
            uint256 number = uint256(randomNumber) % MAX_NUMBER + 1;
            rounds[_round].winningNumbers[i] = number;
        }
        uint num = 5;
        bytes32 randomNumber2 = keccak256(abi.encodePacked(blockhash(drawRound.drawBlock),num));
        uint256 powerBallNumber = uint256(randomNumber2) % MAX_POWERBALL_NUMBER + 1;
        rounds[_round].winningNumbers[5] = powerBallNumber;
    }
    function claim(uint _round) public{
        require(rounds[_round].tickets[msg.sender].length > 0,"You did not play this round");
        require(rounds[_round].winningNumbers[0] != 0,"Winnner has not been chosen");
        uint256 payout = 0;
        uint256[6][] storage balls = rounds[_round].tickets[msg.sender];
        
        // loop through all user tickets
        for (uint i  = 0; i < balls.length; i++){
            uint256 numberMatches = 0;
            for(uint j = 0; j < 5; j++){
                for(uint k = 0; k < 5; k++){
                    if(balls[i][j] == rounds[_round].winningNumbers[k]){
                        numberMatches += 1;
                    } 
                }
            }
            bool powerBallMatch = balls[i][5] == rounds[_round].winningNumbers[5];
            if(numberMatches == 5 && powerBallMatch){
                payout += 50 ether;
            }
            else if (numberMatches == 5){
                payout += 20 ether;
            }
            else if(numberMatches == 4 && powerBallMatch){
                payout += 15 ether;
            }
            else if(numberMatches == 4){
                payout += 10 ether;
            }
            else if(numberMatches == 3 && powerBallMatch){
                payout += 1 ether;
            }else if(numberMatches == 3){
                payout += 1e17;
            }

        }
        delete rounds[_round].tickets[msg.sender];
        payable(msg.sender).transfer(payout);
    
    }
    function getWinningNumbers(uint _round) public view returns (uint256[6] memory){ 
        uint256[6] memory numbers;
        for (uint i = 0; i < rounds[_round].winningNumbers.length; i++){
            numbers[i] = rounds[_round].winningNumbers[i];
        }
        return numbers;
    }
    function kill() public {
        require(msg.sender == owner);
        selfdestruct(payable(owner));
    }

}