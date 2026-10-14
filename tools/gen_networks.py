#!/usr/bin/env python3
"""Regenerate networks.json: the MHDA network name dictionary.

Inputs
  --registry  chains.json from https://chainid.network/chains.json (ethereum-lists/chains)
  --builtin   chains.builtin.json of the wallet; its entries win over the public registry
              (name, testnet flag) and supply every non-EVM family.

Public EVM entries are dropped when the registry marks them deprecated, when the name says so,
or when they publish no RPC. Display names are unique case-insensitively across the whole EVM
list, so an unknown chain can never be shown under the name of a known one.
"""
import argparse, json, re, sys

TESTNET = re.compile(
    r'\b(test|testnet|sepolia|goerli|holesky|hoodi|devnet|amoy|fuji|chiado|alfajores|baklava|'
    r'nile|mumbai|staging|sandbox|preview|regtest|ropsten|rinkeby|kovan|cardona|bepolia|signet|'
    r'localhost|local)\b|testnet', re.I)
DEAD = re.compile(r'deprecat|defunct|shut ?down|sunset|retired|do not use', re.I)
NON_EVM = ['bitcoin', 'tron', 'solana', 'sui', 'ton']


def clean_name(n):
    n = re.sub(r'\s+', ' ', n).strip()
    m = re.sub(r'\s+(Mainnet|Main Network)$', '', n, flags=re.I)
    return m if m else n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', required=True)
    ap.add_argument('--builtin', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    reg = json.load(open(a.registry))
    built = json.load(open(a.builtin))

    evm = {}  # chain_id(int) -> entry
    for c in reg:
        if c.get('status') == 'deprecated' or DEAD.search(c['name']) or not c.get('rpc'):
            continue
        testnet = bool(TESTNET.search(c['name']) or TESTNET.search(c.get('shortName', ''))
                       or TESTNET.search(c.get('chain', '')))
        layer = 'l2' if (c.get('parent') or {}).get('type') == 'L2' else 'l1'
        evm[c['chainId']] = {'name': clean_name(c['name']), 'chain_id': str(c['chainId']),
                             'is_testnet': testnet, 'layer': layer,
                             'ticker': (c.get('nativeCurrency') or {}).get('symbol', '')}

    out = {'version': 1}
    other = {}
    for c in built['chains']:
        if c['network_type'] == 'evm':
            cid = c['chain_id_int']
            e = evm.get(cid, {})
            evm[cid] = {'name': c['title'], 'chain_id': c['chain_id'], 'is_testnet': c['testnet'],
                        'layer': 'l2' if c.get('category') == 'evm_l2' else 'l1',
                        'ticker': c['ticker']}
        else:
            other.setdefault(c['network_type'], []).append(
                {'name': c['title'], 'chain_id': c['chain_id'], 'is_testnet': c['testnet'],
                 'ticker': c['ticker']})

    ours = {c['chain_id_int'] for c in built['chains'] if c['network_type'] == 'evm'}
    seen = {}
    for cid in sorted(evm, key=lambda i: (i not in ours, i)):  # builtin first, then by id
        e = evm[cid]
        key = e['name'].casefold()
        if key in seen:
            e['name'] = '%s (%s)' % (e['name'], e['chain_id'])
            key = e['name'].casefold()
        seen[key] = cid
    out['evm'] = [evm[i] for i in sorted(evm)]
    for nt in NON_EVM:
        out[nt] = other.get(nt, [])
    json.dump(out, open(a.out, 'w'), indent='\t', ensure_ascii=False)
    open(a.out, 'a').write('\n')
    print('evm: %d (%d testnet), other: %s' % (
        len(out['evm']), sum(e['is_testnet'] for e in out['evm']),
        {k: len(out[k]) for k in NON_EVM}), file=sys.stderr)


if __name__ == '__main__':
    main()
