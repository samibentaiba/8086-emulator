; Hello Video Demo — Write directly to CGA video memory at 0xB8000
; Demonstrates direct video memory write (char+attribute pairs)
; Attribute byte: 0x0F = white on black, 0x1E = yellow on blue

DATA SEGMENT
    MSG DB 'HELLO, 8086 WORLD!', '$'
DATA ENDS

CODE SEGMENT
ASSUME CS:CODE, DS:DATA

START:
    ; Initialize DS
    MOV AX, DATA
    MOV DS, AX

    ; Use BIOS INT 10h to set video mode 03h (80x25 color text)
    MOV AH, 00h
    MOV AL, 03h
    INT 10h

    ; Print via DOS INT 21h (AH=09h)
    MOV AH, 09h
    MOV DX, OFFSET MSG
    INT 21h

    ; Write 'H' directly to video memory row 2, col 0 (address 0xB8000 + 2*160)
    MOV AH, 09h          ; Attribute: yellow on blue
    MOV AL, 'H'
    MOV BH, 0            ; Page 0
    MOV BL, 1Eh          ; Attribute byte
    MOV CX, 1
    INT 10h

    ; Terminate
    MOV AH, 4Ch
    INT 21h

CODE ENDS
END START
