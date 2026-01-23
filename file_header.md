# SISC-F FILE HEADER

| OFFSET | SIZE | DESCRIPTION              |
|:------:|:----:|:------------------------:|
|0x0     |0x6   |Magic word. Always SISC-F |
|0x7     |0x2   |Minimum version required  |
|0x9     |0x2   |Program entrypoint address|

It is reccomended not to use addresses 0xC through 0x20 as the header could be expanded. Reccomended program start: 0x50.  
Currently, SISC-F is Little-Endian only. There are plans to integrate big endian support through the header.