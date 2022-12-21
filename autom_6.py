import numpy as np
import serial
import cv2
import time

#---------------------------- Parámetros ------------------------------------------
ti = 23                         # Temperatura inicial [°C]
tf = 190                         # Temperatura final [°C]
paso_t = 0.5                     # Paso de temperatura [°C]
epocas = 1                      # número de "barridos" en que se repite la toma de speckles con las mismas temperaturas
Lamda = 980                     # Longitud de onda [nm]
Z = 12                          # Longitud de zona sensora [mm]
t_est = 20                      # Tiempo de estabilización [seg]
umbral = 0.5                    # Umbral de temperatura aceptable [°C]
data_dir = ''    # Dirección para guardar el dataset

#------------------------------- INCIAR CÁMARA ---------------------------------------

                                # INICIALIZAR CAMARA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11

#----------------------------------PUERTO SERIAL ARDUINO-------------------------------------

mega = serial.Serial(port='ACM0', baudrate=115200, timeout=1, write_timeout=1)

#---------------------------------- Adquisicion -----------------------------------------

temps = np.arange(ti,tf+paso_t,paso_t)                        # Temperaturas a evaluar
num = 0

for k in range(epocas):
    for i in temps:
        num = num + 1

        print('T = ' + str(i) + '°C')
        
        mega.write(str(i).encode('utf-8'))                     # Enviar setpoint de temperatura al arduino
        mega.reset_input_buffer()
        time.sleep(1)
        mega.write(str(i).encode('utf-8'))                     # Enviar setpoint de temperatura al arduino
        mega.reset_input_buffer()                     

        time.sleep(t_est)                                           # Espera tiempo de estabilización (obtenido experimentalmente)
        setpoint=False

        while setpoint == False:
            try:
                mega.write(str(i).encode('utf-8'))                     # Enviar setpoint de temperatura al arduino
                mega.reset_input_buffer()  
                mega.flush()
                T = float(mega.readline().decode("utf-8")[0:-2])
                print(T)
            except:
                print("PAILA")

            if abs(T-i) < umbral:         # Diferencia entre setpoint y temperatura real debe ser menor al umbral
                setpoint = True

        #------------------------Tomar foto Widy Swir---------------------
        Img = np.array(capture())[-1,:,:]                               ## ACA TOMAMOS LA CAPTURA!!!!!!!!!!!!!!!!!!!!!!!!!!
        print("SHAPE:")
        print(Img.shape)
        mega.flush()
        T = float(mega.readline().decode("utf-8")[0:-2])        # Guarda temperatura real

        #---------------------- Guardando dataset en .tiff ---------------
        if T < 100:
            cv2.imwrite(data_dir + 'modesLP_' + str(Lamda) + 'nm_0' + str(T) + 'C_' + str(num) + '.tiff', Img)
        else:
            cv2.imwrite(data_dir + 'modesLP_' + str(Lamda) + 'nm_' + str(T) + 'C_' + str(num) + '.tiff', Img)


mega.write(str(25).encode('utf-8'))                     # Enviar setpoint de temperatura al arduino
mega.close()

# Cerrar camara