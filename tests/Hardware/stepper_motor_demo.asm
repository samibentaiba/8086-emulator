; Stepper Motor Full Revolution Demo — EMU8086 Compatible
; Performs a full 360° clockwise revolution using the EMU8086 half-step sequence on Port 7
; Half-step CW sequence: 0110, 0100, 0011, 0010 (repeating = 32 steps = 360°)

CODE SEGMENT
ASSUME CS:CODE

START:
    MOV CX, 32          ; 32 half-steps = 1 full revolution

STEP_LOOP:
    ; Wait for ready bit (bit 7 of Port 7 IN)
WAIT_READY:
    IN AL, 7
    TEST AL, 80h        ; Check bit 7
    JZ WAIT_READY       ; Not ready — wait

    ; Half-step sequence: 06h → 04h → 03h → 02h → repeat
    MOV AL, 06h         ; Phase: B+C active
    OUT 7, AL
    MOV AL, 04h         ; Phase: C only
    OUT 7, AL
    MOV AL, 03h         ; Phase: A+B active
    OUT 7, AL
    MOV AL, 02h         ; Phase: B only
    OUT 7, AL

    LOOP STEP_LOOP

    ; All coils off
    MOV AL, 00h
    OUT 7, AL

    MOV AH, 4Ch
    INT 21h

CODE ENDS
END START
