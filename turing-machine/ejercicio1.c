#include <stdio.h>

int main() {

    // Recibe cadenas del tipo 0*1*

    char cinta[] = "0011"; // La cadena a leer
    char estado = '0'; // Los estados pueden ser 0, 1, 2 y 3
    // Vamos a tener diferentes condiciones dependiendo del estado y el símbolo a leer
    int i = 0;
    while (estado != '4'){
        printf("%s\n", cinta);

        if(estado == '0'){ // Para el estado 0
            printf("Estado 0: ");
            if(cinta[i] == '0'){
                estado = '1';
                cinta[i] = 'X';
                i++;
            }else if (cinta[i] == 'Y'){
                estado = '3';
                cinta[i] = 'Y';
                i++;
            }else{
                printf("Cadena no válida\n");
                break;
            }
        }else if(estado == '1'){ // Para el estado 1
            printf("Estado 1: ");
            if(cinta[i] == '0'){
                estado = '1';
                cinta[i] = '0';
                i++;
            }else if(cinta[i] == '1'){
                estado = '2';
                cinta[i] = 'Y';
                i--;
            }else if(cinta[i] == 'Y'){
                estado = '1';
                cinta[i] = 'Y';
                i++;
            }else{
                printf("Cadena no válida\n");
                break;
            }
        }else if(estado == '2'){ // Para el estado 2
            printf("Estado 2: ");
            if(cinta[i] == '0'){
                estado = '2';
                cinta[i] = '0';
                i--;
            }else if(cinta[i] == 'X'){
                estado = '0';
                cinta[i] = 'X';
                i++;
            }else if(cinta[i] == 'Y'){
                estado = '2';
                cinta[i] = 'Y';
                i--;
            }else{
                printf("Cadena no válida\n");
                break;
            }
        }else if(estado == '3'){ // Para el estado 3
            printf("Estado 3: ");
            if(cinta[i] == 'Y'){
                estado = '3';
                cinta[i] = 'Y';
                i++;
            }else if(cinta[i] == '\0'){
                estado = '4';
                //cinta[i] = 'B';
                //i++;
                printf("%s\n", cinta);
                printf("Estado 4: Estado de aceptación\n");
            }else{
                printf("Cadena no válida\n");
                break;
            }
        }else{ // Para el estado 4
            printf("Cadena no válida\n");
            break;
        }
    }

    

    return 0;
}

