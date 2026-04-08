SONiVOX FM Synth

# What is this?

I have no idea, but it seems that SONiVOX
had an FM synth in use as GM synthesizer
in some of the phones instead of a sample
based one. Those tables are built based
on source code of aforementioned FM synth.


Algorithms mod table:

### Mode 0

|        | OP1 | OP2 | OP3 | OP4 | Output |
|:------:|:---:|:---:|:---:|:---:|:------:|
|  OP1   | MIX | --- | --- | --- |  [X]   |
|  OP2   | --- | --- | --- | --- |  ----  |
|  OP3   | --- | --- | --- | --- |  [X]   |
|  OP4   | --- | --- | --- | MIX |  [X]   |
| Output | [X] | --- | [X] | [X] |  ----  |
### Mode 1

|        | OP1 | OP2 | OP3 | OP4 | Output |
|:------:|:---:|:---:|:---:|:---:|:------:|
|  OP1   | MIX | --- | --- | --- |  ----  |
|  OP2   | --- | MOD | --- | --- |  ----  |
|  OP3   | --- | --- | --- | --- |  [X]   |
|  OP4   | --- | --- | --- | MIX |  [X]   |
| Output | --- | --- | [X] | [X] |  ----  |

### Mode 2

|        | OP1 | OP2 | OP3 | OP4 | Output |
|:------:|:---:|:---:|:---:|:---:|:------:|
|  OP1   | MIX | --- | --- | --- |  ----  |
|  OP2   | --- | MOD | --- | --- |  ----  |
|  OP3   | --- | --- | --- | --- |  ----  |
|  OP4   | --- | --- | --- | MOD |  [X]   |
| Output | --- | --- | --- | [X] |  ----  | 
### Mode 3

|        | OP1 | OP2 | OP3 | OP4 | Output |
|:------:|:---:|:---:|:---:|:---:|:------:|
|  OP1   | M+X | --- | --- | --- |  ----  |
|  OP2   | --- | MOD | --- | --- |  ----  |
|  OP3   | --- | --- | OUT | --- |  [X]   |
|  OP4   | --- | --- | --- | --- |  ----  |
| Output | --- | --- | [X] | --- |  ----  | 

### Mode 4

|        | OP1 | OP2 | OP3 | OP4 | Output |
|:------:|:---:|:---:|:---:|:---:|:------:|
|  OP1   | MOD | --- | --- | --- |  ----  |
|  OP2   | --- | MOD | --- | --- |  ----  |
|  OP3   | --- | --- | --- | --- |  ----  |
|  OP4   | --- | --- | --- | MOD |  ----  |
| Output | --- | --- | --- | --- |  ----  | 

### Mode 5

|        | OP1 | OP2 | OP3 | OP4 | Output |
|:------:|:---:|:---:|:---:|:---:|:------:|
|  OP1   | MIX | --- | --- | --- |  ----  |
|  OP2   | --- | MOD | --- | --- |  ----  |
|  OP3   | --- | --- | --- | --- |  ----  |
|  OP4   | --- | --- | --- | MOD |  ----  |
| Output | --- | --- | --- | --- |  ----  | 