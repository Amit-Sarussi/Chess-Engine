# Chess Engine

A high-performance chess engine built using bitboards for efficient move generation and evaluation. It features a neural network-based AI that trains itself through reinforcement learning and self-play.

## Optimizations

- **Bitboard Move Generation** – Uses 64-bit integers for fast, efficient move calculations. [Chess Programming - Bitboards](https://www.chessprogramming.org/Bitboards)

- **Magic Bitboards** – Maps blockers to legal moves instantly for sliding pieces. [Chess Programming - Magic bitboards](https://www.chessprogramming.org/Magic_Bitboards)

- **Precomputed Tables** – Stores attack patterns to avoid redundant calculations. [Chess Programming - Attack maps](https://www.chessprogramming.org/Attack_and_Defend_Maps)

- **Fast Sliding Attacks** – Uses magic bitboards for quick, constant-time lookups. [Chess Programming - Use of Magic bitboards](https://www.chessprogramming.org/Magic_Bitboards#How_it_works)

- **Bitwise Masking** – AND operations filter legal moves and detect obstructions. [Chess Programming - Bitwise Operations](https://www.chessprogramming.org/General_Setwise_Operations)
