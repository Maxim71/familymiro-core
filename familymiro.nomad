job "familymiro-cluster" {
  datacenters = ["dc1"]
  type        = "service"

  group "itr-apps" {
    count = 1

    # 🛸 ВЕТВЛЕНИЕ СЕТЕВОЙ КАРТЫ: Жестко фиксируем порт 8050 в ОЗУ хостинга
    network {
      port "http" {
        static = 8050
      }
    }

    task "fastapi-director" {
      driver = "docker"

      config {
        image = "python:3.10-slim"
        # Запуск bash-конвейера: ставим ИТР-библиотеки и поднимаем асинхронный FastAPI-сервер
        command = "bash"
        args    = ["-c", "pip install --no-cache-dir fastapi uvicorn pydantic && python3 -m uvicorn ezhik_api:app --host 0.0.0.0 --port 8050"]
        ports   = ["http"]
        
        # Монтируем кодовую базу сервера внутрь Docker-контейнера для сквозного чтения
        volumes = [
            "/root/app:/root/app"
        ]
      }

      resources {
        cpu    = 300 # Всего 300 MHz
        memory = 128 # Всего 128 MB ОЗУ! Легче Kubernetes в 30 раз.
      }
    }
  }
}
