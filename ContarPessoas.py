import cv2
import picamera
import imutils
import numpy as np
import time
import os
import Adafruit_DHT
import RPi.GPIO as GPIO

pino_sensor = 2
sensor = Adafruit_DHT.DHT11
GPIO.setmode(GPIO.BCM)
statusAr = False

led_ligado = 3
led_desligado = 4
GPIO.setup(led_ligado, GPIO.OUT)
GPIO.setup(led_desligado, GPIO.OUT)

GPIO.output(led_ligado, GPIO.LOW)
GPIO.output(led_desligado, GPIO.HIGH)


def detect(frame):
    (humans, _) = HOGCV.detectMultiScale(frame,  
                                    winStride=(5, 5), 
                                    padding=(8, 8), 
                                    scale=1.30)
    for (x, y, w, h) in humans: 
        cv2.rectangle(frame, (x, y),  
                      (x + w, y + h),  
                      (0, 255, 0), 2)
        
    cv2.putText(frame, 'Status : Detectando... ', (20,20), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255,0,0), 2)
    cv2.putText(frame, "Total Pessoas : {}".format(str(len(humans))), (30,40), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255,0,0), 2)
    
    cv2.imwrite('/home/pi/Desktop/detected.jpeg', frame)
    cv2.imshow('Camera', frame)
    cv2.waitKey(100)
    
    return len(humans)

def LigaAr():
    print('Ligando o Ar...')
    os.system('irsend SEND_ONCE AR KEY_0')
    GPIO.output(led_ligado, GPIO.HIGH)
    GPIO.output(led_desligado, GPIO.LOW)
    return True

def DesligaAr():
    print('Desligando o Ar.. ')
    os.system('irsend SEND_ONCE AR KEY_0')
    GPIO.output(led_ligado, GPIO.LOW)
    GPIO.output(led_desligado, GPIO.HIGH)
    return False

def getTemperatura():
    
    print("*** Lendo os valores de temperatura. ***")

    while(True):
        umid, temp = Adafruit_DHT.read_retry(sensor, pino_sensor)
        if umid is not None and temp is not None:
            print('Temperatura atual do ambiente: ',temp)
            break
        else:
            print("Falha ao ler dados do DHT11 !!!")
    
    return temp

def temperaturaIdeal(nPessoas):
    
    if nPessoas > 0 and nPessoas < 6:
        return 25
    elif nPessoas > 5 and nPessoas < 11:
        return 24
    elif nPessoas > 10 and nPessoas < 16:
        return 23
    elif nPessoas > 15 and nPessoas < 21:
        return 22
    elif nPessoas > 20 and nPessoas < 26:
        return 21
    elif nPessoas > 25:
        return 20
    
def abaixarTemp(tmp):
    os.system('irsend SEND_ONCE AR KEY_0')
    
    
def aumentarTemp(tmp):
    os.system('irsend SEND_ONCE AR KEY_0')
    

def detectByPathImage(path,sts):
    image = cv2.imread(path)
    image = imutils.resize(image, width = min(500, image.shape[1])) 
    TotalPessoas = detect(image)
    
    print('Total de pessoas:', TotalPessoas)
    
    if TotalPessoas > 0:
        if not sts:
            #liga o ar
            sts = LigaAr()
            #detectar temperatura do ambiente
            tempAmbiente = getTemperatura()
            # verifica a temperatura ideal para o ambiente
            tempIdeal = temperaturaIdeal(TotalPessoas)
            print('Temperatura ideal: ',tempIdeal)
            
             #verificando a temperatura
            if tempAmbiente > tempIdeal:
                #abaixa a temperatura
                print("abaixando temperatura para: ",tempIdeal)
                abaixarTemp(tempIdeal)
            elif tempAmbiente < tempIdeal:
                #aumenta a temperatura
                print("aumentando a temperatura para: ",tempIdeal)
                aumentarTemp(tempIdeal)

        else:
            #detectar temperatura do ambiente
            tempAmbiente = getTemperatura()
            
            # verifica a temperatura ideal para o ambiente
            tempIdeal = temperaturaIdeal(TotalPessoas)
            print('Temperatura ideal: ',tempIdeal)
            
            #verificando a temperatura
            if tempAmbiente > tempIdeal:
                #abaixa a temperatura
                print("abaixando temperatura para: ",tempIdeal)
                abaixarTemp(tempIdeal)
            elif tempAmbiente < tempIdeal:
                #aumenta a temperatura
                print("aumentando a temperatura para: ",tempIdeal)
                aumentarTemp(tempIdeal)

    else:
        if sts:
            #deliga o ar
            sts = DesligaAr()
            
       
        
    return sts  
    
    
def detectByCamera(status):
    
    with picamera.PiCamera() as camera:
        while True:
            print('Detectando pessoas...')
            #camera.capture('/home/pi/Desktop/original.jpeg')
            status = detectByPathImage('/home/pi/Desktop/original.jpeg',status)
            

    camera.close()
    cv2.destroyAllWindows()
    
    
    

if __name__ == "__main__":
    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    print('[INFO] Conectando...')
    detectByCamera(statusAr)


