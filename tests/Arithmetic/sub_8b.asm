;program to subtract two 8b numbers
NAME Arithmetic
TITLE sub_8b
; Test Passed
assume cs:code,ds:data
data segment
    num1 db ?
    num2 db ?
    res db ?
    msg1 db 10,13,"enter the first number: $"
    msg2 db 10,13,"enter the second number: $"
    msg3 db 10,13,"result of subtraction is: $"
data ends   


code segment
    start: mov ax,data
           mov ds,ax           ;initialize data segment 
           
           lea dx,msg1         ;load address of msg1 into dx
           mov ah,9h           ;interrupt to display contents of dx
           int 21h    
           
           mov ah,1h           ;read a character from console
           int 21h
           sub al,30h          ;convert number into bcd from ascii form
           mov num1,al         ;store number as num1
           
           lea dx,msg2         ;load address of msg2 into dx
           mov ah,9h           ;interrupt to display contents of dx
           int 21h    
           
           mov ah,1h           ;read a character from console
           int 21h
           sub al,30h          ;convert number into bcd from ascii form
           mov num2,al         ;store number as num2
           
           mov al,num1         
           sub al,num2         ;sub num2 from num1
           mov res,al          ;save signed difference while displaying the prompt
           lea dx,msg3         ;print ms3
           mov ah,9h
           int 21h
           
           mov al,res
           cmp al,0
           jge magnitude
           mov dl,'-'
           mov ah,2h
           int 21h
           mov al,res
           neg al
magnitude: aam                 ;split magnitude into decimal tens and units
           add ax,3030h        ;convert both digits to ASCII
           mov bx,ax
           mov ah,2h           ;print first digit
           mov dl,bh                                
           int 21h
           
           mov ah,2            ;print second digit
           mov dl,bl
           int 21h
    
           mov ah,4ch
           int 21h
    
code ends
end start
