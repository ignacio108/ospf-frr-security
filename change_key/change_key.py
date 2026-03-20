import os
import subprocess
import sys
import argparse
from datetime import datetime, timedelta



'''
README:

Este script realiza un cambio de claves en un lapso de tiempo que definimos.

La lógica del cambio de claves es la siguiente

Key en uso(key_id):
                    desde           hasta
accept lifetime     date-time       date+time
send   lifetime     date-time       date+time

Key nueva(key_id+1):
                    desde           hasta
accept lifetime     date            infinite
send   lifetime     date            infinite

'''


#Función para restarle a nuestro tiempo actual (año,mes,dia,hora,minutos,segundos) un tiempo dado (dia,hora,minutos,segundos)
def subtract_time(current_time, time_to_substract):

    current_dt=datetime(int(current_time[0]),int(current_time[1]),int(current_time[2]),int(current_time[3]),int(current_time[4]),int(current_time[5]))

    time_delta=timedelta(days=int(time_to_substract[0]),hours=int(time_to_substract[1]),minutes=int(time_to_substract[2]),seconds=int(time_to_substract[3]))

    new_time=current_dt-time_delta

    '''
    f"": define una string formateada, permitiendo insertar variables directamente dentro del texto usando llaves {}.

    new_time.second: es el valor que representa los segundos (por ejemplo, 7).

        :02: esta parte es un formato específico que significa:

        0: añade ceros a la izquierda si el número tiene menos dígitos que el ancho especificado.

        2: asegura que el número tenga siempre dos dígitos de ancho.
    
    '''
    return [new_time.year, new_time.month, new_time.day, f"{new_time.hour:02}", f"{new_time.minute:02}", f"{new_time.second:02}"]


#Función para sumarle a nuestro tiempo actual (año,mes,dia,hora,minutos,segundos) un tiempo dado (dia,hora,minutos,segundos)
def add_time(current_time, time_to_substract):

    current_dt=datetime(int(current_time[0]),int(current_time[1]),int(current_time[2]),int(current_time[3]),int(current_time[4]),int(current_time[5]))

    time_delta=timedelta(days=int(time_to_substract[0]),hours=int(time_to_substract[1]),minutes=int(time_to_substract[2]),seconds=int(time_to_substract[3]))

    new_time=current_dt+time_delta

    return [new_time.year, new_time.month, new_time.day, f"{new_time.hour:02}", f"{new_time.minute:02}", f"{new_time.second:02}"]


def main():

    parser = argparse.ArgumentParser(description='Script para implementar un cambio de claves sin perder las vecindades')
    parser.add_argument('--key',nargs='*', default=[], help='Lista con los siguientes argumentos: [Nombre del Key-chain, Key_id en uso, Clave_nueva]')
    parser.add_argument('--routername', nargs='*',default=[], help='Lista con el nombre de los routers a modificar')
    parser.add_argument('--time', help='tiempo en segundos para el cambio de claves, habrá un tiempo minimo de 60 segundos')
    args = parser.parse_args()

    print(args.routername)
    #Comprobamos que los argumentos son correctos
    if(len(args.key)!=3):
        print("Argumento key inválido, tiene que ser una array de dos elementos: [Nombre del Key-chain, Key_id en uso, Clave_nueva]")
        sys.exit(1)
    
    #Comprobamos que se ha introducido al menos un equipo, y si es all se modificarán todos los equipos del escenario
    if(len(args.routername)==0):
        print("Argumento routername inválido, tiene que ser una array de al menos un elemento")
        sys.exit(1)
    elif(len(args.routername)==1 and args.routername[0]=="all"):
        router_list = ["rA","rB","rC","rd","rE"]
    else:
        router_list=args.routername



    try:
        input_time=int(args.time)
    except ValueError:
        print("Argumento time inválido, tiene que ser un número entero")
        sys.exit(1)

    finally:
        # Mapa de números de mes a nombres en inglés
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        # Mapa de números de mes a nombres en inglés con el formato de linux
        month_names_linux = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }

        #Convertimos nuestro tiempo en horas minutos y segundos
        days = input_time // 86400
        hours = (input_time % 86400) // 3600
        minutes = (input_time % 3600) // 60
        seconds = input_time % 60

        if(input_time<30):
            input_time=[0,0,0,30]
        else:
            input_time=[days,hours,minutes,seconds]



        for i,rname in enumerate(router_list):
            print(f'Realizando el proceso de cambio de claves de {rname}')
            obtain_date=subprocess.check_output(["lxc-attach",rname,"--","date"])
            obtain_month=subprocess.check_output(["lxc-attach",rname,"--","date","+%m"])
            obtain_year=subprocess.check_output(["lxc-attach",rname,"--","date","+%Y"])
            
            aux_date_decoded= obtain_date.decode('utf-8').rsplit()
            aux_month_decoded=obtain_month.decode('utf-8').rsplit()
            aux_year_decoded=obtain_year.decode('utf-8').rsplit()
            
            actual_time=aux_year_decoded+aux_month_decoded + aux_date_decoded[1].split(":") + aux_date_decoded[4].split(":")
            
            #Caculamos nuestro tiempo_actual - input_time
            date_minus_time=subtract_time(actual_time, input_time)

            date_plus_time=add_time(actual_time, input_time)

            #Implementamos un accept lifetime y send lifetime en la key en uso para que eventualmente deje de utilizarse.

            os.system(f'lxc-attach {rname} -- vtysh -c "conf t" -c "key chain {args.key[0]}" -c "key {args.key[1]}" -c "accept-lifetime {date_minus_time[3]}:{date_minus_time[4]}:{date_minus_time[5]} {month_names.get(date_minus_time[1])} {date_minus_time[2]} {date_minus_time[0]} {date_plus_time[3]}:{date_plus_time[4]}:{date_plus_time[5]} {month_names.get(date_plus_time[1])} {date_plus_time[2]} {date_plus_time[0]}"')
            os.system(f'lxc-attach {rname} -- vtysh -c "conf t" -c "key chain {args.key[0]}" -c "key {args.key[1]}" -c "send-lifetime {date_minus_time[3]}:{date_minus_time[4]}:{date_minus_time[5]} {month_names.get(date_minus_time[1])} {date_minus_time[2]} {date_minus_time[0]} {date_plus_time[3]}:{date_plus_time[4]}:{date_plus_time[5]} {month_names.get(date_plus_time[1])} {date_plus_time[2]} {date_plus_time[0]}"')

            #Creamos una nueva key con los accept y send lifetime adecuados
            os.system(f'lxc-attach {rname} -- vtysh -c "conf t" -c "key chain {args.key[0]}" -c "key {str(int(args.key[1])+1)}" -c "key-string {args.key[2]}"')
            os.system(f'lxc-attach {rname} -- vtysh -c "conf t" -c "key chain {args.key[0]}" -c "key {str(int(args.key[1])+1)}" -c "cryptographic-algorithm hmac-sha-256"')
            os.system(f'lxc-attach {rname} -- vtysh -c "conf t" -c "key chain {args.key[0]}" -c "key {str(int(args.key[1])+1)}" -c "accept-lifetime {actual_time[3]}:{actual_time[4]}:{actual_time[5]} {month_names_linux.get(actual_time[1])} {actual_time[2]} {actual_time[0]} infinite"')
            os.system(f'lxc-attach {rname} -- vtysh -c "conf t" -c "key chain {args.key[0]}" -c "key {str(int(args.key[1])+1)}" -c "send-lifetime {actual_time[3]}:{actual_time[4]}:{actual_time[5]} {month_names_linux.get(actual_time[1])} {actual_time[2]} {actual_time[0]} infinite"')


if __name__ == "__main__":
    main()