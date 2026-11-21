# tiny-chess-01 entry

A chess engine in at most 4,096 bytes of Python (main.py), written for the
make.fun tiny-chess-01 bounty. main.py is an lzma-packed build of the engine
source developed in this repository's history: a 0x88 board, negamax
alpha-beta search with a transposition table, quiescence search with check
evasions, check extensions, late move reduction, MVV-LVA ordering and a
material + piece-square evaluation, searching to a fixed node budget so
every move is deterministic.

Run: the engine talks to the competition env over HTTP
(MAKEFUN_ENV_URL), as the bounty rules describe.
