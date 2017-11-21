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

    chain.wait.for_receipt(cm_coin.transact({'from':accounts[1], 'value':1}).tap(accounts[2]))

    # Tapping the wrong person should not do anything:
    assert cm_coin.call().balanceOf(accounts[1]) == 0

    assert cm_coin.call().unit() == unit;

    assert cm_coin.call().balanceOf(accounts[0]) == dev_supply
    assert cm_coin.call().totalSupply() == dev_supply

    assert cm_coin.call().amITheOne()
    assert not cm_coin.call({'from': accounts[2]}).amITheOne()

    assert cm_coin.call().taps() == 0

    # rightful tap
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[1]}).tap(accounts[0]))
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
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[2]}).tap(accounts[0], 'huhu'))

    assert cm_coin.call().taps() == 1
    assert cm_coin.call().comments() == 0


    # tapping with comment
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[2]}).tap(accounts[1], 'huhu'))

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

    assert cm_coin.call().badassComments(0) == 'huhu'


    # tapping with comment
    chain.wait.for_receipt(cm_coin.transact({'from':accounts[3]}).tap(accounts[2], 'hahu'))

    assert cm_coin.call().balanceOf(accounts[2]) > 0

    assert cm_coin.call().cumulativeTime(accounts[0]) > 10
    assert cm_coin.call().cumulativeTime(accounts[0]) < 20

    assert cm_coin.call().cumulativeTime(accounts[1]) > 10
    assert cm_coin.call().cumulativeTime(accounts[1]) < 30

    assert cm_coin.call().cumulativeTime(accounts[2]) > 10
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

    assert cm_coin.call().badassComments(0) == 'huhu'
    assert cm_coin.call().badassComments(1) == 'hahu'
