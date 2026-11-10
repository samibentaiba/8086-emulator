NAME TrafficLights
TITLE traffic_lights_test

; Virtual Traffic Light Hardware Verification Test
; Port 4 - EMU8086 Standard Specification

assume cs:codesg, ds:datasg

codesg segment
start:
    ; Initialize data segment
    mov ax, datasg
    mov ds, ax

    ; 1. All Red pattern: 0000 0010 0100 1001b = 0249H
    mov ax, 0249h
    out 4, ax

    ; 2. Read back state from port 4 into BX to verify IN instruction
    in bx, 4

    ; 3. North & South Green (bits 2, 8), East & West Red (bits 3, 9)
    ; Pattern: 0000 0011 0000 1100b = 030Ch
    mov ax, 030ch
    out 4, ax

    ; 4. North & South Yellow (bits 1, 7), East & West Red (bits 3, 9)
    ; Pattern: 0000 0010 1000 1010b = 028Ah
    mov ax, 028ah
    out 4, ax

    ; 5. All Red clearance
    mov ax, 0249h
    out 4, ax

    ; 6. East & West Green (bits 5, 11), North & South Red (bits 0, 6)
    ; Pattern: 0000 1000 0110 0001b = 0861h
    mov ax, 0861h
    out 4, ax

    ; 7. East & West Yellow (bits 4, 10), North & South Red (bits 0, 6)
    ; Pattern: 0000 0100 0101 0001b = 0451h
    mov ax, 0451h
    out 4, ax

    ; 8. Test 8-bit output (OUT 4, AL)
    mov al, 09h
    out 4, al

    ; 9. Terminate program with return code 0
    mov ah, 4ch
    mov al, 00h
    int 21h

codesg ends

datasg segment
    dummy db 0
datasg ends

end start
