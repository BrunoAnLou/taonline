from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from datetime import time as tt
import time 
import os
import glob2
import xlwings as xw
import pandas as pd
import shutil

while True:

    hora_atual = datetime.now()
    previsao = hora_atual + timedelta(minutes=10)
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-dev-shm-usage")
    chromedriver_path = 'C:\\Users\\p739492\\Projetos\\Drivers\\chromedriver.exe'
    cservice =  webdriver.ChromeService(executable_path=chromedriver_path)
    navegador = webdriver.Chrome(service = cservice, options=options)

    try:
        

        link = "http://curitiba.callcenter.caixa/manager/"
        relatorio = "http://curitiba.callcenter.caixa/manager/rpc.php?s=rage&busca=1&check=1&fila_search=&fila_all=on&agente_search=&agente_all=on&tipo=detalhado&mostrar_logados=tudo&periodo=4&dtde={data}2024-04-15&dtate=2024-04-15&de=0000000000&ate=2359590000&voltar=1&module=rage&cmd=export&type=excel"
        download = 'chrome://downloads/' 

        navegador.get(link)

        navegador.switch_to.default_content()
        navegador.switch_to.frame(navegador.find_element(By.TAG_NAME, 'iframe'))
        print("iniciando")

        ##Aguada username aparecer na tela
        WebDriverWait(navegador, 10).until(EC.visibility_of_element_located((By.ID, 'username')))

        navegador.find_element(By.ID, 'username').send_keys("P739492")
        navegador.find_element(By.ID, 'passwd').send_keys("130116")
        navegador.find_element(By.CLASS_NAME, 'login-submit').click()
        print('Logando')
        time.sleep(3)


        WebDriverWait(navegador, 10).until(EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), "Painel")) 

        navegador.find_element(By.XPATH, '//*[@id="srel"]/a/span').click()
        time.sleep(2)
        print("Clicando perf")
        navegador.find_element(By.XPATH, '//*[@id="srel"]/div/div/div/div[1]/div/ul/li[1]/a').click()


        WebDriverWait(navegador, 10).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/span/form/div/div[3]/div[1]/div/div[1]/div[1]/select')))
        ##seleciona detalhado
        navegador.find_element(By.XPATH, '/html/body/div[5]/div/span/form/div/div[3]/div[1]/div/div[1]/div[1]/select').click()
        navegador.find_element(By.XPATH, '/html/body/div[5]/div/span/form/div/div[3]/div[1]/div/div[1]/div[1]/select/option[2]').click()

        ##CLICA EM PESQUISAR
        navegador.find_element(By.XPATH, '/html/body/div[5]/div/span/form/div/div[3]/div[2]/button').click()


        print("Começando a coleta")

        WebDriverWait(navegador, 900).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/span/div[1]/div/div/div[2]/a/button')))
        time.sleep(2)
        navegador.find_element(By.XPATH, '/html/body/div[5]/div/span/div[1]/div/div/div[2]/a/button').click()

        print("Baixou")
        ##navegador.execute_script("window.open('http://curitiba.callcenter.caixa/manager/rpc.php?s=rage&busca=1&check=1&fila_search=&fila_all=on&agente_search=&agente_all=on&tipo=detalhado&mostrar_logados=tudo&periodo=4&dtde=2024-04-15&dtate=2024-04-15&de=1713236400&ate=1713322799&voltar=1&module=rage&cmd=export&type=excel', 'new window')")
        time.sleep(5)

        
        #####################################  ENCONTRANDO ARQUIVO ORIGEM ##########################################
        diretorio = 'C:\\Users\\p739492\\Downloads'
        destino_relatorio = 'C:\\Users\\p739492\\Projetos\\TA_ONLINE\\aaa.csv'
        listar = glob2.glob(os.path.join(diretorio, '*.xls'))

        arquivo_recente= max(listar,key=os.path.getctime)

        print("arquivo mais recente é: ", arquivo_recente)
        ####### TRANSFERINDO O ARQUIVO ####################
        df = pd.read_html(arquivo_recente, header = 0)[0]

        df['HORA_LOGIN'] = pd.to_datetime(df['HORA_LOGIN'], format="%H:%M:%S").dt.time

        limite = tt(2,0,0)

        df_filtro = df[df['HORA_LOGIN'] > limite]

        print('a')
        print('proxima atualização em: ', previsao.strftime("%H:%M"))
        df_filtro.to_csv(destino_relatorio, index=False)

        
        os.remove(arquivo_recente)
        navegador.quit()
        time.sleep(60)

        print("finalizou")
        
    except Exception as e:
        print("Foi de santos", e)
        navegador.quit()
        navegador = webdriver.Chrome(service = cservice, options=options)
        
print('Crashou')