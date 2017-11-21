/*
* This is the source code of the smart contract for the SOUL token, aka Soul Napkins.
* Copyright 2017 and all rights reserved by the owner of the following Ethereum address:
* 0x10E44C6bc685c4E4eABda326c211561d5367EEec
*/

pragma solidity ^0.4.18;

// ERC Token standard #20 Interface
// https://github.com/ethereum/EIPs/issues/20
contract ERC20Interface {

    // Token symbol
    string public symbol;

    // Name of token
    string public name;

    // Decimals of token
    uint8 public decimals;

    // Total token supply
    function totalSupply() public constant returns (uint256 supply);

    // The balance of account with address _owner
    function balanceOf(address _owner) public constant returns (uint256 balance);

    // Send _value tokens to address _to
    function transfer(address _to, uint256 _value) public returns (bool success);

    // Send _value tokens from address _from to address _to
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);

    // Allow _spender to withdraw from your account, multiple times, up to the _value amount.
    // If this function is called again it overwrites the current allowance with _value.
    // this function is required for some DEX functionality
    function approve(address _spender, uint256 _value) public returns (bool success);

    // Returns the amount which _spender is still allowed to withdraw from _owner
    function allowance(address _owner, address _spender) public constant returns (uint256 remaining);

    // Triggered when tokens are transferred.
    event Transfer(address indexed _from, address indexed _to, uint256 _value);

    // Triggered whenever approve(address _spender, uint256 _value) is called.
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);
}


// Implementation of ERC20Interface
contract ERC20Token is ERC20Interface{

    // account balances
    mapping(address => uint256) internal balances;

    // Owner of account approves the transfer of amount to another account
    mapping(address => mapping (address => uint256)) internal allowed;

    // Function to access acount balances
    function balanceOf(address _owner) public constant returns (uint256) {
        return balances[_owner];
    }

    // Transfer the _amount from msg.sender to _to account
    function transfer(address _to, uint256 _amount) public returns (bool) {
        if (balances[msg.sender] >= _amount && _amount > 0
                && balances[_to] + _amount > balances[_to]) {
            balances[msg.sender] -= _amount;
            balances[_to] += _amount;
            Transfer(msg.sender, _to, _amount);
            return true;
        } else {
            return false;
        }
    }

    // Send _value amount of tokens from address _from to address _to
    // The transferFrom method is used for a withdraw workflow, allowing contracts to send
    // tokens on your behalf, for example to "deposit" to a contract address and/or to charge
    // fees in sub-currencies; the command should fail unless the _from account has
    // deliberately authorized the sender of the message via some mechanism; we propose
    // these standardized APIs for approval:
    function transferFrom(
        address _from,
        address _to,
        uint256 _amount
    ) public returns (bool) {
        if (balances[_from] >= _amount
            && allowed[_from][msg.sender] >= _amount && _amount > 0
                && balances[_to] + _amount > balances[_to]) {
            balances[_from] -= _amount;
            allowed[_from][msg.sender] -= _amount;
            balances[_to] += _amount;
            Transfer(_from, _to, _amount);
            return true;
        } else {
            return false;
        }
    }

    // Allow _spender to withdraw from your account, multiple times, up to the _value amount.
    // If this function is called again it overwrites the current allowance with _value.
    function approve(address _spender, uint256 _amount) public returns (bool) {
        allowed[msg.sender][_spender] = _amount;
        Approval(msg.sender, _spender, _amount);
        return true;
    }

    // Function to specify how much _spender is allowed to transfer on _owner's behalf
    function allowance(address _owner, address _spender) public constant returns (uint256) {
        return allowed[_owner][_spender];
    }

}


contract CatchMeCoin is ERC20Token {

    // Token symbol
    string public symbol = 'CMT';

    // Name of token
    string public name = 'Catch Me Tokens';

    // Decimals of token
    uint8 public decimals = 9;

    // smallest unit
    uint256 public constant unit = 10**9;

    // tokens awarded per second of ownership
    uint256 public constant perSecond = 10**6;

    // cumulative time each address was owner of the coin
    mapping(address => uint256) public cumulativeTime;

    // optional comments people can leave
    mapping(uint256 => string) public badassComments;

    mapping(uint256 => uint256) private badassIDs;
    mapping(uint256 => string) private IDsToUsernames;

    // logs if username is taken
    mapping(string => bool) private usernamesTaken;

    // maps addresses to usernames
    mapping(address => uint256) private addressesToIDs;

    // number or registered users
    uint256 private users;

    // number of comments
    uint256 public comments;

    // number of total taps
    uint256 public taps;

    // owner of contract
    address public owner;

    // time of last tap
    uint256 private lastTap;

    // contains the coin owners
    mapping(address => bool) private coinOwners;

    // total supply of tokens
    // increased with every tap
    uint256 private internalSupply;


    function CatchMeCoin(){
        owner = msg.sender;
        lastTap = now;
        coinOwners[owner] = true;
        // dev supply
        internalSupply = 3600 * unit;
        balances[owner] = internalSupply;
        Transfer(this, owner, internalSupply);
    }

    function () public payable{
        // just take donations
    }

    function withdraw() public{
        // send donations to owner
        require(msg.sender == owner);
        owner.transfer(this.balance);
    }

    function totalSupply() public constant returns (uint256){
        return internalSupply;
    }

    function amITheOne() public constant returns(bool){
        return coinOwners[msg.sender];
    }

    // taps an opponent and reassigns the coin and awards tokens
    // in case target was the previous coin owner
    function tap(address target, string badassComment, string username) public payable returns(bool){
        if (coinOwners[target]){
            uint256 awardedTokens;
            uint256 timeDelta = now - lastTap;

            // you cannot tap yourself
            require(target != msg.sender);

            // store badass comment
            if (bytes(badassComment).length > 0){
                addComment(badassComment, username);
            }
            // remember the taps
            taps += 1;
            // award tokens
            awardedTokens = timeDelta * perSecond;
            internalSupply += awardedTokens;
            balances[target] += awardedTokens;
            // keep a cumulative sum of time target owned the coin
            cumulativeTime[target] += timeDelta;
            // now we have a new last tap
            lastTap = now;
            // change ownership of coin
            coinOwners[target] = false;
            coinOwners[msg.sender] = true;

            Transfer(this, target, awardedTokens);

            return true;
        }
        return false;
    }

    // tap without comment
    function tap(address target) public payable returns(bool){
        return tap(target, "", "");
    }

    function whatsMyUsername() public constant returns(string username){
        uint256 userID = addressesToIDs[msg.sender];
        username = IDsToUsernames[userID];
        return username;
    }

    function badassUsername(uint256 commentID) public constant returns(string username){
        uint256 userID = badassIDs[commentID];
        username = IDsToUsernames[userID];
        return username;
    }

    function addComment(string comment, string username) private {
        uint256 userID;
        uint256 commentID;

        if (bytes(username).length > 0){
            // if new username is provided check that user does not
            // exist, yet;
            require(!usernamesTaken[username]);

            users += 1;
            userID = users;

            addressesToIDs[msg.sender] = userID;
            IDsToUsernames[userID] = username;
            usernamesTaken[username] = true;
        } else {

            userID = addressesToIDs[msg.sender];
            // user must exist
            require(userID > 0);
        }

        comments += 1;
        commentID = comments;
        // comment 0 is empty
        badassComments[commentID] = comment;
        badassIDs[commentID] = userID;

    }

}