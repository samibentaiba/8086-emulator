NAME VideoTest
TITLE video_text_mode_test

; Verification of CGA 80x25 Text Mode Display @ 0xB8000 & BIOS INT 10H

assume cs:codesg, ds:datasg, es:extraseg

codesg segment
start:
    ; Initialize data segment
    mov ax, datasg
    mov ds, ax

    ; 1. Set Video Mode 03h (80x25 Color Text) via INT 10H
    mov ah, 00h
    mov al, 03h
    int 10h

    ; 2. Set cursor to Row 2, Column 5
    mov ah, 02h
    mov bh, 00h
    mov dh, 02h
    mov dl, 05h
    int 10h

    ; 3. Print '8', '0', '8', '6' using Teletype output (INT 10H, AH=0Eh)
    mov ah, 0eh
    mov bl, 0eh     ; Yellow on Black
    mov al, '8'
    int 10h
    mov al, '0'
    int 10h
    mov al, '8'
    int 10h
    mov al, '6'
    int 10h

    ; 4. Direct video memory access @ 0xB8000 (ES:DI)
    ; Point ES to video segment 0xB800
    mov ax, 0b800h
    mov es, ax

    ; Write 'C' with Light Green attribute (0Ah) at Row 4, Col 5 (Offset = 2 * (4 * 80 + 5) = 650 = 028Ah)
    mov di, 028ah
    mov byte ptr es:[di], 'C'
    mov byte ptr es:[di+1], 0ah

    ; Write 'P' with Light Green attribute at Col 6
    mov byte ptr es:[di+2], 'P'
    mov byte ptr es:[di+3], 0ah

    ; Write 'U' with Light Green attribute at Col 7
    mov byte ptr es:[di+4], 'U'
    mov byte ptr es:[di+5], 0ah

    ; 5. DOS INT 21H version check
    mov ah, 30h
    int 21h

    ; 6. Terminate program
    mov ah, 4ch
    mov al, 00h
    int 21h

codesg ends

datasg segment
    dummy db 0
datasg ends

extraseg segment
    extra_dummy db 0
extraseg ends

end start
