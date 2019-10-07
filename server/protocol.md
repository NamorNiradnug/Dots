# Dots Net Protocol Specification
Port: `5722`
## Data types
    boolean:
        byte isTrue:
            isTrue != 0

    char:
        byte[2] data:
            chr((byte[0] << 8) | byte[1])

    int:
        byte[4] bytes:
            (byte[0] << 24) | (byte[1] << 16) | (byte[2] << 8) | byte[3]

    String:
        byte length
        char[length] chars:
            ''.join(chars)

## Packet structure
    byte type
    int length
    byte[length] payload
    byte zero = 0

## Packet types
    -ID- NAME:
        PAYLOAD             - DESCRIPTION (DIRECTION)

    0x00 FIND:
        String nickname     - the sender's nickname (serverbound)
                            - the other player's nickname (clientbound)
        boolean playFirst   - wether the receiver plays first (clientbound)

    0x01 PLAY:
        int x, y            - coordinates of the sender's move (serverbound)
                            - coordinates of the other player's move (clientbound)

    0x04 TIE

    0x05 SURRENDER

    0x07 END:
        boolean win         - wether the receiver won (clientbound)

    0x7F CONFIRM:
        boolean success     - wether the operation succeeded (both)

    0xFF ERROR:
        String reason       - reason for the error (clientbound)

## Procedures
The client initiating the procedure is `cl1`.
The server is `sr`.
The other client is `cl2`.

### Search for players
1. cl1 -> sr: FIND
2. sr -> cl1: CONFIRM(true)
3. cl2 -> sr: FIND
4. sr -> cl2: CONFIRM(true)
5. sr -> cl1: FIND(cl2.nickname)
6. sr -> cl2: FIND(cl1.nickname)

### Play
1. cl1 -> sr: PLAY
2. sr -> cl1: CONFIRM
3. sr -> cl2: PLAY(cl1.x, cl1.y)
4. cl2 -> sr: CONFIRM

### Tie
1. cl1 -> sr: TIE
2. sr -> cl1: CONFIRM
3. sr -> cl2: TIE
4. cl2 -> sr: CONFIRM
5. End

### Surrender
1. cl1 -> sr: SURRENDER
2. sr -> cl1: CONFIRM
3. sr -> cl2: SURRENDER
4. cl2 -> sr: CONFIRM
5. End

### End
1. sr -> cl1: END
2. sr -> cl2: END
3. Disconnect

### Error
1. sr -> cl1: ERROR
2. sr -> cl2: ERROR
3. Disconnect