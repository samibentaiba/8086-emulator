; Traffic Lights Full Cycle Demo — EMU8086 Compatible
; Cycles through a standard North/South + East/West traffic pattern on Port 4
; Port 4 bit layout: bits 0-2=North(RYG), 3-5=West(RYG), 6-8=South(RYG), 9-11=East(RYG)

CODE SEGMENT
ASSUME CS:CODE

START:
    ; --- Phase 1: North+South GREEN, East+West RED ---
    ; North=Green(bit2), South=Green(bit8), East=Red(bit9), West=Red(bit3)
    MOV AX, 0100100100100b  ; N:G=1,W:R=1,S:G=1,E:R=1  => bits 2,3,8,9
    OUT 4, AX
    MOV CX, 0FFFFh
DELAY1: LOOP DELAY1

    ; --- Phase 2: North+South YELLOW, East+West RED ---
    MOV AX, 0100010010010b  ; N:Y,W:R,S:Y,E:R
    OUT 4, AX
    MOV CX, 03FFFh
DELAY2: LOOP DELAY2

    ; --- Phase 3: All RED ---
    MOV AX, 0001001001001b  ; N:R,W:R,S:R,E:R
    OUT 4, AX
    MOV CX, 02000h
DELAY3: LOOP DELAY3

    ; --- Phase 4: East+West GREEN, North+South RED ---
    MOV AX, 0100100100100b
    OUT 4, AX
    MOV CX, 0FFFFh
DELAY4: LOOP DELAY4

    ; --- Phase 5: East+West YELLOW, North+South RED ---
    MOV AX, 0100010010010b
    OUT 4, AX
    MOV CX, 03FFFh
DELAY5: LOOP DELAY5

    ; --- Phase 6: All OFF ---
    MOV AX, 0000h
    OUT 4, AX

    MOV AH, 4Ch
    INT 21h

CODE ENDS
END START
