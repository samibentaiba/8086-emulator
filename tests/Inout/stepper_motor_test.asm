NAME StepperMotor
TITLE stepper_motor_test

; Virtual Stepper Motor Hardware Verification Test
; Port 7 - EMU8086 Standard Specification

assume cs:codesg, ds:datasg

codesg segment
start:
    mov ax, datasg
    mov ds, ax

    ; 1. Wait until motor is ready
wait_ready:
    in al, 7
    test al, 80h
    jz wait_ready

    ; 2. Clockwise (CW) rotation sequence
    ; Step 1: 0110b (6)
    mov al, 06h
    out 7, al

    ; Step 2: 0100b (4)
    mov al, 04h
    out 7, al

    ; Step 3: 0011b (3)
    mov al, 03h
    out 7, al

    ; Step 4: 0010b (2)
    mov al, 02h
    out 7, al

    ; Step 5: 0110b (6)
    mov al, 06h
    out 7, al

    ; Step 6: 0100b (4)
    mov al, 04h
    out 7, al

    ; Step 7: 0011b (3)
    mov al, 03h
    out 7, al

    ; Step 8: 0010b (2)
    mov al, 02h
    out 7, al

    ; 3. Counter-Clockwise (CCW) rotation sequence
    ; Step 9: 0011b (3)
    mov al, 03h
    out 7, al

    ; Step 10: 0001b (1)
    mov al, 01h
    out 7, al

    ; Step 11: 0110b (6)
    mov al, 06h
    out 7, al

    ; Step 12: 0010b (2)
    mov al, 02h
    out 7, al

    ; 4. Verify motor status via IN instruction
    in al, 7

    ; 5. Terminate program
    mov ah, 4ch
    mov al, 00h
    int 21h

codesg ends

datasg segment
    dummy db 0
datasg ends

end start
