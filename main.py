from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence, TYPE_RELATIVE_TIMELOCK, \
    TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.script import Script
from identity import Id
from helper import hash256, print_tx, gen_secret
from typing import List


def main():
    """
    Run main to print the size of the different transactions to the console
    """
    rand = ''
    for i in range(0, 32):
        rand += gen_secret()
    # Some addresses on the testnet
    id_u0 = Id(
        'e120477e329a0f15bcf975c86181828f2e015bfe34e2efe9af6362c8d53a13e2')  # addr: mxiFd6G7RbpJY6sdUhMknT78hTDPJUdE3e
    id_u0_stealth = Id(
        'e12049bc238a0f15bcf576c86171828f3e0363cb2ac2efe9af6362c8d53a22c5')  # addr: mzRZKnpNRshmi6pNUaHc1gxrpnp4UVpdX5
    id_u1 = Id(
        'e12046ad146a0f15bcf974c86181828f1e0472ea1bd2efe9af6362c8d53a41a7')  # addr: mwhZnxZYLJQa6uPWn2qLF9J3jDiauH4BwT
    id_u1_stealth = Id(
        'e12046ad146a0f15bcf973c86181828f1e0472ea1bd2efe9af6362c8d54b42b7')  # addr: mxDNMmPPgpXEwVw9HZoF2Zck9UjGW9cnDp
    id_multi_01 = Id(
        'e12046ad246a0f15bef982c86181828f1e0472ea1bd2efe9af6362c8d53a41b8')  # addr: mp3X5j5adS6XnwrfBJ4JB4QMzFetMMXKCd
    id_u2 = Id(
        'e12046ad146a0f15bcf975c86181828f1e0472ea1bd2e3a3af6362c8d53a71e5')  # addr: muRD4ggRmuLNZYzW6tfBoHJHRKyk4KstCy
    id_multi_12 = Id(
        'e12046ad246a0f15bcf982c86181828f1d0372ea1bd2efe9af6362c8d53a82c1')  # addr: mozySLpwxEpzGt5RDumEG8uRVqWaA2RGRt
    id_u2_stealth = Id(
        'e12046ad146a0f15bcf973c86172828f1e0472ea1be2efe9bc2743c8d54b42b7')  # addr: mpRJrRQcVQSNxoYZ6dQ9uf1gtHSiZp7G77

    tx_state_in = TxInput('98f209d606ea0e5222ae2296e310fc0f96741f083eb0fe6ca5ff3c6a277217bf', 0) # 0.01 BTC = 1000000 satoshi
    tx_er_in = TxInput('ad38ac30504e7a6c08f9ec20b2544ab9be24172617e5724dc69c27481d4a3719', 1) # 0.00022 BTC = 22000 satoshi

    fee = 100
    eps = 1
    n=2
    t=10
    delta=2
    a=100000
    balLeft=500000
    balRight=500000

    txerintx = get_txer_in_tx(tx_er_in, id_u0, id_u0_stealth, 2*fee+n*eps)
    print_tx(txerintx, 'txerintx')
    txer = get_txer(tx_er_in, id_u0, [id_u0_stealth], fee, eps)
    print_tx(txer, 'tx_er 1 ouput')
    txer = get_txer(tx_er_in, id_u0, [id_u0_stealth, id_u1_stealth], fee, eps)
    print_tx(txer, 'tx_er 2 outputs')
    txer = get_txer(tx_er_in, id_u0, [id_u0_stealth, id_u1_stealth, id_u2_stealth], fee, eps)
    print_tx(txer, 'tx_er 3 outputs')
    tx_state = get_state(tx_state_in, id_multi_01, id_u0, id_u1, a, balLeft, balRight, fee, t, delta)
    print_tx(tx_state, 'tx_state') # 313 Bytes, 225 Bytes without Contract. 88 Bytes for contract. Saves 31 Bytes
    tx_refund = get_tx_refund(TxInput(txer.get_hash(), 0), TxInput(tx_state.get_hash(), 0), id_u0, id_u0_stealth, id_multi_01, 100000, 2*fee)
    print_tx(tx_refund, 'tx_refund')
    tx_pay = get_tx_pay(TxInput(tx_state.get_hash(), 0), id_u1, a, 2*fee)
    print_tx(tx_pay, 'tx_pay')
    ####
    random = rand
    tx_stateLN = get_state_LN(tx_state_in, id_multi_01, id_u0,id_u1, a, balLeft, balRight, fee, hash256(random), t)
    print_tx(tx_stateLN, 'tx_stateLN') #344 Bytes, 225 Bytes without HTLC. 119 Bytes for HTLC.
    tx_LN_pay = get_tx_LN_pay(tx_state_in, id_u1, id_multi_01, a, 2*fee, random)
    print_tx(tx_LN_pay, 'tx_LN_pay')
    tx_LN_refund = get_tx_LN_refund(tx_state_in, id_u0, id_multi_01, a, 2*fee)
    print_tx(tx_LN_refund, 'tx_LN_refund')


def get_state(tx_in0: TxInput, id_multisig: Id, id_l: Id, id_r: Id, a: float, x_left: float, x_right: float,
              fee: float, t: int, delta: int = 0x02) -> Transaction:
    old_script = Script(['OP_DUP',
                                        id_multisig.pk.to_hex(), 'OP_CHECKSIG', 'OP_IF', delta,
                                        'OP_CHECKSEQUENCEVERIFY', 'OP_ELSE',
                                        id_r.pk.to_hex(), 'OP_CHECKSIG', 'OP_IF', t, 'OP_CHECKLOCKTIMEVERIFY',
                                        'OP_ELSE', 'OP_RETURN', 'OP_ENDIF', 'OP_ENDIF']) # requires scriptsig: multisig  or r_sig

    new_script = Script(['OP_IF',
            id_multisig.pk.to_hex(), 'OP_CHECKSIGVERIFY', delta, 'OP_CHECKSEQUENCEVERIFY',
            'OP_ELSE',
            id_r.pk.to_hex(), 'OP_CHECKSIGVERIFY', t, 'OP_CHECKLOCKTIMEVERIFY',
            'OP_ENDIF', 0x1]) # requires scriptsig: multisig, 0x1 or r_sig, 0x0

    tx_out0 = TxOutput(a, new_script)
    tx_out1 = TxOutput(x_left - a - fee, id_l.p2pkh)
    tx_out2 = TxOutput(x_right, id_r.p2pkh)

    tx = Transaction([tx_in0], [tx_out0, tx_out1, tx_out2])

    sig_multisig = id_multisig.sk.sign_input(tx, 0, id_multisig.p2pkh)

    tx_in0.script_sig = Script([sig_multisig, id_multisig.pk.to_hex()])

    return tx

def get_txer_in_tx(tx_in: TxInput, id_sender: Id, id_sender_stealth: Id, a: float) -> Transaction:
    # tx_in must hold at least n times eps coins plus a fee
    tx_out0 = TxOutput(a, id_sender_stealth.p2pkh)

    tx_er_in = Transaction([tx_in], [tx_out0])

    sig_sender = id_sender.sk.sign_input(tx_er_in, 0, id_sender.p2pkh)

    tx_in.script_sig = Script([sig_sender, id_sender.pk.to_hex()])

    return tx_er_in

def get_txer(tx_in: TxInput, id_sender: Id, id_list: List[Id], fee: float, eps: float = 1) -> Transaction:
    # tx_in must hold at least n times eps coins plus a fee
    out_list = [] #[tx_out0]
    for id in id_list:
        out_list.append(TxOutput(eps, id.p2pkh))

    txEr = Transaction([tx_in], out_list)

    sig_sender = id_sender.sk.sign_input(txEr, 0, id_sender.p2pkh)

    tx_in.script_sig = Script([sig_sender, id_sender.pk.to_hex()])

    return txEr

def get_tx_refund(tx_in_txer: TxInput, tx_in_state: TxInput, id_left: Id, id_left_stealth: Id, id_multisig: Id, a: float, fee: float, eps: float = 1) -> Transaction:
    # tx_in must hold at least n times eps coins plus a fee
    tx_out0 = TxOutput(a+eps-fee, id_left.p2pkh)

    tx = Transaction([tx_in_txer, tx_in_state], [tx_out0])

    sig_left_stealth = id_left_stealth.sk.sign_input(tx, 0, id_left_stealth.p2pkh)
    sig_multi = id_multisig.sk.sign_input(tx, 0, id_multisig.p2pkh)

    tx_in_txer.script_sig = Script([sig_left_stealth, id_left_stealth.pk.to_hex()])
    tx_in_state.script_sig = Script([sig_multi, 0x1])

    return tx

def get_tx_pay(tx_in_state: TxInput, id_right: Id, a: float, fee: float) -> Transaction:
    # tx_in must hold at least n times eps coins plus a fee
    tx_out0 = TxOutput(a-fee, id_right.p2pkh)

    tx = Transaction([tx_in_state], [tx_out0])

    sig_right = id_right.sk.sign_input(tx, 0, id_right.p2pkh)

    tx_in_state.script_sig = Script([sig_right, 0x0])

    return tx

## Lightning:
def get_state_LN(tx_in0: TxInput, id_multisig: Id, id_l: Id, id_r: Id, a: float, x_left: float, x_right: float,
              fee: float, hashedsecret, t: int) -> Transaction:

    old_script = Script(['OP_DUP',
                                        id_l.pk.to_hex(), 'OP_CHECKSIG', 'OP_IF', t,
                                        'OP_CHECKLOCKTIMEVERIFY', 'OP_ELSE',
                                        id_r.pk.to_hex(), 'OP_CHECKSIG', 'OP_IF', 'OP_HASH256', hashedsecret,
                                        'OP_EQUALVERIFY', 'OP_ELSE', 'OP_RETURN', 'OP_ENDIF', 'OP_ENDIF'])

    new_script = Script(['OP_IF',
            id_l.pk.to_hex(), 'OP_CHECKSIGVERIFY', t, 'OP_CHECKLOCKTIMEVERIFY',
            'OP_ELSE',
            id_r.pk.to_hex(), 'OP_CHECKSIGVERIFY', 'OP_HASH256', hashedsecret, 'OP_EQUALVERIFY',
            'OP_ENDIF'])

    tx_out0 = TxOutput(a, new_script)
    tx_out1 = TxOutput(x_left - a - fee, id_l.p2pkh)
    tx_out2 = TxOutput(x_right, id_r.p2pkh)

    tx = Transaction([tx_in0], [tx_out0, tx_out1, tx_out2])

    sig_multisig = id_multisig.sk.sign_input(tx, 0, id_multisig.p2pkh)

    tx_in0.script_sig = Script([sig_multisig, id_multisig.pk.to_hex()])

    return tx

def get_tx_LN_pay(tx_in_state: TxInput, id_right: Id, id_multi: Id, a: float, fee: float, secret) -> Transaction:
    # tx_in must hold at least n times eps coins plus a fee
    tx_out0 = TxOutput(a-fee, id_right.p2pkh)

    tx = Transaction([tx_in_state], [tx_out0])

    sig_multi = id_multi.sk.sign_input(tx, 0, id_multi.p2pkh)

    tx_in_state.script_sig = Script([secret, sig_multi, 0x0])

    return tx

def get_tx_LN_refund(tx_in_state: TxInput, id_left: Id, id_multi: Id, a: float, fee: float) -> Transaction:
    # tx_in must hold at least n times eps coins plus a fee
    tx_out0 = TxOutput(a-fee, id_left.p2pkh)

    tx = Transaction([tx_in_state], [tx_out0])

    sig_multi = id_multi.sk.sign_input(tx, 0, id_multi.p2pkh)

    tx_in_state.script_sig = Script([sig_multi, 0x1])

    return tx

if __name__ == "__main__":
    main()
