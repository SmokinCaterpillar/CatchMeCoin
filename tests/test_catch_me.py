from ethereum.tester import TransactionFailed
from ethereum.exceptions import InvalidTransaction
import pytest
import time

ether = int(1e18)
finney = int(ether/1000)

decimals = 9
unit = int(1e9)
per_second = int(1e6)

dev_supply = 3600 * unit

null_address = '0x0000000000000000000000000000000000000000'

def get_wei(chain, accounts):
    """ Returns the wei for each address in `accounts`

    :param chain: populus chain interface
    :param accounts: List of adresses
    :return: List of weis
    """
    web3 = chain.web3
    weis = []
    for irun, account in enumerate(accounts):
        wei = web3.eth.getBalance(accounts[irun])
        weis.append(wei)
    return weis


def test_init(chain, accounts):

    provider = chain.provider
    cm_coin, deploy_txn_hash = provider.get_or_deploy_contract(
        'CatchMeCoin'
    )

    # Check some initial settings:
    assert cm_coin.call().owner() == accounts[0]
    assert cm_coin.call().balanceOf(accounts[1]) == 0

    assert cm_coin.call().name() == 'Catch Me Tokens'
    assert cm_coin.call().symbol() == 'CMT'
    assert cm_coin.call().decimals() == decimals
    assert cm_coin.call().unit() == unit;

    assert cm_coin.call().balanceOf(accounts[0]) == dev_supply
    assert cm_coin.call().totalSupply() == dev_supply

    assert cm_coin.call().amITheOne()
    assert not cm_coin.call({'from': accounts[2]}).amITheOne()

    assert cm_coin.call().taps() == 0
    assert cm_coin.call().comments() == 0


def test_tap(chain, accounts):
    provider = chain.provider
    cm_coin, deploy_txn_hash = provider.get_or_deploy_contract(
        'CatchMeCoin'
    )
    start = time.time()

    #startTap = cm_coin.call().lastTap();

    # should fail cannot tap self
    with pytest.raises(TransactionFailed):
        chain.wait.for_receipt(cm_coin.transact({'from':accounts[0], 'value':1}).tap(accounts[0]))

    res = chain.wait.for_receipt(cm_coin.transact({'from':accounts[1], 'value':1}).tap(accounts[2]))

    # Tapping the wrong person should not do anything:
    assert cm_coin.call().balanceOf(accounts[1]) == 0

    assert cm_coin.call().unit() == unit;

    assert cm_coin.call().balanceOf(accounts[0]) == dev_supply
    assert cm_coin.call().totalSupply() == dev_supply

    assert cm_coin.call().amITheOne()
    assert not cm_coin.call({'from': accounts[2]}).amITheOne()

    assert cm_coin.call().taps() == 0

    # rightful tap
    res2 = chain.wait.for_receipt(cm_coin.transact({'from':accounts[1]}).tap(accounts[0]))
    end = time.time()

    # Tapping the wrong person should not do anything:
    assert cm_coin.call().balanceOf(accounts[1]) == 0
    assert cm_coin.call().balanceOf(accounts[0]) > \
           dev_supply + (end - start) * per_second

    assert cm_coin.call().cumulativeTime(accounts[0]) > 10
    assert cm_coin.call().cumulativeTime(accounts[0]) < 20

    #assert cm_coin.call().lastTap() > startTap

    stuff = (end - start + 20) * per_second
    assert cm_coin.call().balanceOf(accounts[0]) < dev_supply + stuff
    assert cm_coin.call().totalSupply() > dev_supply

    assert cm_coin.call().totalSupply() == cm_coin.call().balanceOf(accounts[0])

    assert not cm_coin.call().amITheOne()
    assert cm_coin.call({'from': accounts[1]}).amITheOne()

    assert cm_coin.call().taps() == 1
    assert cm_coin.call().comments() == 0


    # tapping the wrong person
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[2]}).tap(accounts[0], 'huhu', 'acc2'))

    assert cm_coin.call().taps() == 1
    assert cm_coin.call().comments() == 0


    # tapping with comment
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[2]}).tap(accounts[1], 'huhu', 'acc2'))

    assert cm_coin.call().balanceOf(accounts[1]) > 0

    assert cm_coin.call().cumulativeTime(accounts[0]) > 10
    assert cm_coin.call().cumulativeTime(accounts[0]) < 20

    assert cm_coin.call().cumulativeTime(accounts[1]) > 10
    assert cm_coin.call().cumulativeTime(accounts[1]) < 30

    assert cm_coin.call().balanceOf(accounts[0]) > dev_supply

    assert cm_coin.call().totalSupply() == \
           cm_coin.call().balanceOf(accounts[0]) + \
           cm_coin.call().balanceOf(accounts[1])

    assert not cm_coin.call().amITheOne()
    assert not cm_coin.call({'from': accounts[1]}).amITheOne()
    assert cm_coin.call({'from': accounts[2]}).amITheOne()


    assert cm_coin.call().taps() == 2
    assert cm_coin.call().comments() == 1

    assert cm_coin.call().badassComments(1) == 'huhu'

    # tapping with comment
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[3]}).tap(accounts[2], 'hahu', 'acc3'))

    assert cm_coin.call().balanceOf(accounts[2]) > 0

    assert cm_coin.call().cumulativeTime(accounts[0]) > 10
    assert cm_coin.call().cumulativeTime(accounts[0]) < 20

    assert cm_coin.call().cumulativeTime(accounts[1]) > 10
    assert cm_coin.call().cumulativeTime(accounts[1]) < 30

    assert cm_coin.call().cumulativeTime(accounts[2]) > 5
    assert cm_coin.call().cumulativeTime(accounts[2]) < 20

    assert cm_coin.call().balanceOf(accounts[0]) > dev_supply

    assert cm_coin.call().totalSupply() == \
           cm_coin.call().balanceOf(accounts[0]) + \
           cm_coin.call().balanceOf(accounts[1]) + \
           cm_coin.call().balanceOf(accounts[2])

    assert not cm_coin.call().amITheOne()
    assert not cm_coin.call({'from': accounts[1]}).amITheOne()
    assert not cm_coin.call({'from': accounts[2]}).amITheOne()
    assert cm_coin.call({'from': accounts[3]}).amITheOne()


    assert cm_coin.call().taps() == 3
    assert cm_coin.call().comments() == 2

    assert cm_coin.call().badassComments(1) == 'huhu'
    assert cm_coin.call().badassComments(2) == 'hahu'

    assert cm_coin.call().badassUsername(1) == 'acc2'
    assert cm_coin.call().badassUsername(2) == 'acc3'

    assert cm_coin.call({'from':accounts[2]}).whatsMyUsername() == 'acc2'
    assert cm_coin.call({'from':accounts[5]}).whatsMyUsername() == ''


def test_comments(chain, accounts):
    provider = chain.provider
    cm_coin, deploy_txn_hash = provider.get_or_deploy_contract(
        'CatchMeCoin'
    )
    start = time.time()

    #startTap = cm_coin.call().lastTap();

    # should fail cannot tap self
    with pytest.raises(TransactionFailed):
        chain.wait.for_receipt(cm_coin.transact({'from':accounts[0], 'value':1}).tap(accounts[0]))

    chain.wait.for_receipt(cm_coin.transact({'from':accounts[1], 'value':1}).tap(accounts[2], 'ladida', 'acc1'))

    # rightful tap
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[1]}).tap(accounts[0], 'ladida', 'acc1'))

    assert cm_coin.call().comments() == 1


    # tapping the wrong person
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[2]}).tap(accounts[0], 'huhu', 'acc2'))

    assert cm_coin.call().taps() == 1
    assert cm_coin.call().comments() == 1
    assert cm_coin.call({'from':accounts[1]}).amITheOne()

    chain.wait.for_receipt(cm_coin.transact({'from':accounts[2]}).tap(accounts[1], 'hihi', 'acc2'))
    # tapping again with different username
    with pytest.raises(TransactionFailed):
        chain.wait.for_receipt(cm_coin.transact({'from':accounts[1]}).tap(accounts[2], 'haha', 'acc666'))

    # tapping again with same username
    with pytest.raises(TransactionFailed):
        chain.wait.for_receipt(cm_coin.transact({'from':accounts[1]}).tap(accounts[2], 'haha', 'acc1'))

    assert cm_coin.call({'from':accounts[2]}).amITheOne()

    # username taken
    with pytest.raises(TransactionFailed):
        chain.wait.for_receipt(cm_coin.transact({'from':accounts[3]}).tap(accounts[2], 'hihi', 'acc1'))

    assert cm_coin.call().usernameTaken('acc1')
    assert not cm_coin.call().usernameTaken('acc3')

    # tapping with comment
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[1]}).tap(accounts[2], 'rrrr'))

    assert cm_coin.call({'from':accounts[1]}).amITheOne()

    assert cm_coin.call().taps() == 3
    assert cm_coin.call().comments() == 3

    assert cm_coin.call().badassComments(1) == 'ladida'
    assert cm_coin.call().badassComments(2) == 'hihi'
    assert cm_coin.call().badassComments(3) == 'rrrr'

    assert cm_coin.call().badassUsername(1) == 'acc1'
    assert cm_coin.call().badassUsername(2) == 'acc2'
    assert cm_coin.call().badassUsername(3) == 'acc1'


def test_fallback(chain, accounts):
    provider = chain.provider
    cm_coin, deploy_txn_hash = provider.get_or_deploy_contract(
        'CatchMeCoin'
    )

    web3 = chain.web3

    chain.wait.for_receipt(web3.eth.sendTransaction({'value':100*ether,
                                                     'from':accounts[1],
                                                     'to': cm_coin.address,
                                                     'gas':200000}))

    assert web3.eth.getBalance(cm_coin.address) == int(100*ether)

    with pytest.raises(TransactionFailed):
        chain.wait.for_receipt(cm_coin.transact({'from':accounts[1]}).withdraw())

    before = web3.eth.getBalance(accounts[0])
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[0]}).withdraw())
    after = web3.eth.getBalance(accounts[0])

    assert after > before
    assert after > before + 99*ether
    assert after < before + 110*ether


def test_donate(chain, accounts):
    provider = chain.provider
    cm_coin, deploy_txn_hash = provider.get_or_deploy_contract(
        'CatchMeCoin'
    )

    chain.wait.for_receipt(cm_coin.transact({'from':accounts[1], 'value':50*ether}).tap(accounts[2]))

    web3 = chain.web3

    with pytest.raises(TransactionFailed):
        chain.wait.for_receipt(cm_coin.transact({'from':accounts[5]}).withdraw())

    before = web3.eth.getBalance(accounts[0])
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[0]}).withdraw())
    after = web3.eth.getBalance(accounts[0])

    assert after > before
    assert after > before + 49*ether
    assert after < before + 60*ether


def test_token_transfer(chain, accounts):
    provider = chain.provider

    soul_token, deploy_txn_hash2 = provider.get_or_deploy_contract(
        'CatchMeCoin'
    )

    assert soul_token.call().balanceOf(accounts[0]) == dev_supply

    # does nothing because of insufficient funds
    chain.wait.for_receipt(soul_token.transact().transfer(accounts[1], int(19925*unit)))
    assert soul_token.call().balanceOf(accounts[0]) == dev_supply

    # transfer the tokens
    chain.wait.for_receipt(soul_token.transact().transfer(accounts[1], int(25*unit)))

    # check that transfer worled
    assert soul_token.call().balanceOf(accounts[0]) == dev_supply - int(25*unit)
    assert soul_token.call().balanceOf(accounts[1]) == int(25*unit)

    # approve some future transfers
    chain.wait.for_receipt(soul_token.transact().approve(accounts[2], int(50*unit)))

    # check for to large sending
    chain.wait.for_receipt(soul_token.transact({'from': accounts[2]}).transferFrom(accounts[0],
                                                                                 accounts[1],
                                                                                 int(51*unit)))

    # there should be no transfer because the amount was too large
    assert soul_token.call().balanceOf(accounts[0]) == dev_supply - int(25*unit)
    assert soul_token.call().balanceOf(accounts[1]) == int(25*unit)

    # this should be allowed
    chain.wait.for_receipt(soul_token.transact({'from': accounts[2]}).transferFrom(accounts[0],
                                                                                 accounts[1],
                                                                                 int(25*unit)))

    assert soul_token.call().balanceOf(accounts[0]) == dev_supply - int(50*unit)
    assert soul_token.call().balanceOf(accounts[1]) == int(50*unit)
    assert soul_token.call().allowance(accounts[0], accounts[2]) == int(25*unit)

    # this should be allowed
    chain.wait.for_receipt(soul_token.transact({'from': accounts[2]}).transferFrom(accounts[0],
                                                                                 accounts[1],
                                                                                 int(25*unit)))

    assert soul_token.call().balanceOf(accounts[0]) == dev_supply - int(75*unit)
    assert soul_token.call().balanceOf(accounts[1]) == int(75*unit)
    assert soul_token.call().allowance(accounts[0], accounts[2]) == 0