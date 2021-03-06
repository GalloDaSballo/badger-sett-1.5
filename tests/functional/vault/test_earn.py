import brownie
from brownie import *
from helpers.constants import MaxUint256

from dotmap import DotMap
import pytest


def test_earn(deploy_complete, deployer, governance, rando, keeper):

    want = deploy_complete.want
    vault = deploy_complete.vault
    strategy = deploy_complete.strategy

    # Deposit
    assert want.balanceOf(deployer) > 0
    assert want.balanceOf(rando) > 0

    # no balance in vault
    assert vault.balance() == 0

    # no inital shares of deployer / rando
    assert vault.balanceOf(deployer) == 0
    assert vault.balanceOf(rando) == 0

    depositAmount_deployer = int(want.balanceOf(deployer) * 0.01)
    assert depositAmount_deployer > 0

    depositAmount_rando = int(want.balanceOf(rando) * 0.01)
    assert depositAmount_rando > 0

    want.approve(vault.address, MaxUint256, {"from": deployer})
    want.approve(vault.address, MaxUint256, {"from": rando})

    # Deposit for deployer and earn

    vault.deposit(depositAmount_deployer, {"from": deployer})

    # Trying to call earn from unauthorized actors should fail
    with brownie.reverts("onlyAuthorizedActors"):
        vault.earn({"from": rando})

    available_before_earn = (
        vault.available()
    )  # this amount should be deposited into the strategy
    vault.earn({"from": governance})

    assert strategy.balanceOf() == available_before_earn

    # Now rando user deposits and earn

    vault.deposit(depositAmount_rando, {"from": rando})

    before_earn_balance_strat = strategy.balanceOf()
    available_before_earn = (
        vault.available()
    )  # this amount should be deposited into the strategy
    vault.earn({"from": governance})

    after_earn_balance_strat = strategy.balanceOf()

    assert after_earn_balance_strat - before_earn_balance_strat == available_before_earn

    # When vault is paused earn should fail

    vault.deposit(depositAmount_deployer, {"from": deployer})

    vault.pause({"from": governance})

    assert vault.paused() == True

    with brownie.reverts("Pausable: paused"):
        vault.earn({"from": governance})
