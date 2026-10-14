# AirNox common

Shared data for the AirNox desktop wallet and the phone app.

## networks.json

The MHDA network name dictionary. A UI looks a chain up by `(network family, chain_id)` and shows
`name`; the raw `chain_id` is shown only when the pair is missing here.

- `evm`: every non-deprecated EVM network of the public registry (chainid.network), L1 and L2,
  mainnets and testnets, plus the wallet's own networks (their names win). `chain_id` is the decimal
  EIP-155 id as a string. Display names are unique case-insensitively, so an unknown chain cannot
  borrow the name of a known one; a clash gets ` (<chain_id>)` appended.
- `bitcoin`, `tron`, `solana`, `sui`, `ton`: the families the wallet supports. Their `chain_id` is
  the MHDA `ci` slot the wallet itself assigns (`mainnet`, `devnet`, `bitcoin_testnet`, ...): these
  networks do not hand one out, so it is formed locally.
- `layer` (`l1` / `l2`) and `is_testnet` are hints; `is_testnet` is guessed from the name for public
  entries.
