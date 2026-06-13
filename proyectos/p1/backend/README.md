



crear un entorno para trabajar con python
```
python3 -m venv venv
```


activar el entorno:
```
source venv/bin/activate
```


Instalar FastAPI y Uvicorn
```
pip install "fastapi[standard]" uvicorn
```


para generar un requirement.txt automatico:
```
pip freeze > requirements.txt
```


Ejecutar servidor
```
uvicorn main:app --reload
```






# como hacer lo del bot
1 telegram


1 hacer el grupo --> "nombre"
 

 1 ir a botFather

 /newbot
 2) nombre

 3) nombre_bot

 4) https://api.telegram.org/bot{TOKEN_BOT}}/getUpdates

 5) instalar:
 "
 ```
(venv) gio@gio:~/Documentos/26S1/vacas/ia1_1S26V/-IA1-_VACASJUN2026_GiovanniConcoha_202100229/proyectos/p1/backend$ pip install requests
Collecting requests
  Downloading requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
Collecting charset_normalizer<4,>=2 (from requests)
  Downloading charset_normalizer-3.4.7-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 40.9/40.9 kB 458.6 kB/s eta 0:00:00
Requirement already satisfied: idna<4,>=2.5 in ./venv/lib/python3.12/site-packages (from requests) (3.18)
Requirement already satisfied: urllib3<3,>=1.26 in ./venv/lib/python3.12/site-packages (from requests) (2.7.0)
Requirement already satisfied: certifi>=2023.5.7 in ./venv/lib/python3.12/site-packages (from requests) (2026.5.20)
Downloading requests-2.34.2-py3-none-any.whl (73 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 73.1/73.1 kB 901.1 kB/s eta 0:00:00
Downloading charset_normalizer-3.4.7-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (216 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 216.6/216.6 kB 2.7 MB/s eta 0:00:00
Installing collected packages: charset_normalizer, requests
Successfully installed charset_normalizer-3.4.7 requests-2.34.2
(venv) gio@gio:~/Documentos/26S1/vacas/ia1_1S26V/-IA1-_VACASJUN2026_GiovanniConcoha_202100229/proyectos/p1/backend$ pip install python-dotenv
Requirement already satisfied: python-dotenv in ./venv/lib/python3.12/site-packages (1.2.2)
(venv) gio@gio:~/Documentos/26S1/vacas/ia1_1S26V/-IA1-_VACASJUN2026_GiovanniConcoha_202100229/proyectos/p1/backend$


 ```
 
 "



