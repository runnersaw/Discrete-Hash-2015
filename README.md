# Discrete Hash 2015
We're creating a new hash function, providing software that performs the hash, as well as testing the hash for different types of attacks. 

Our hash function uses the Merkle-Damgård construction.

## Collisions

We found a collision attack for the current hash function. The two inputs XXXXXXX0 00000000 00001000 XXXXXXX1 and XXXXXXX0 00000001 00000111 XXXXXXX1 will have the same output if the first 8 and the last 8 bits are the same with both inputs.

This hash function is not suitable for cryptographic use. 
