

backend/

app/

├── main.py

├── config
│   └── db.py

├── models/
│   ├── categoria.py
│   ├── consulta.py
│   ├── palabra_clave.py
│   ├── pregunta.py
│   ├── telegram_chat.py
│   └── usuario.py

├── repositories/
│   ├── categoria_repository.py
│   ├── consulta_repository.py
│   ├── pregunta_repository.py
│   ├── telegram_chat_repository.py
│   └── usuario_repository.py

├── services/
│   ├── pregunta_service.py
│   ├── categoria_service.py
│   ├── auth_service.py
│   ├── telegram_service.py
│   └── bot_service.py

├── controllers/
│   ├── pregunta_controller.py
│   ├── categoria_controller.py
│   ├── auth_controller.py
│   ├── telegram_controller.py
│   └── webhook_controller.py

└── utils/
    └── helpers.py