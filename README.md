# 📰 Yogonet Scraper - Scraping + BigQuery + Cloud Run

Este proyecto realiza scraping del sitio [Yogonet International](https://www.yogonet.com/international/), procesando los artículos destacados y cargándolos en una tabla de BigQuery. Todo el flujo corre de forma automatizada mediante un **Cloud Run Job** en Google Cloud.

---

## 🚀 Tecnologías utilizadas

- **Python 3.10**
- **Selenium**
- **Pandas**
- **Google BigQuery**
- **Google Cloud Run Jobs**
- **Docker**
- **dotenv**

---

## 📌 ¿Qué hace este proyecto?

- Realiza scraping de los artículos destacados en el home de Yogonet.
- Extrae título, bajada, imagen, y link de cada artículo.
- Calcula metadatos del título como:
  - Cantidad de palabras
  - Cantidad de caracteres
  - Palabras con mayúscula inicial
- Limpia duplicados utilizando el link como identificador único.
- Carga los datos resultantes a una tabla de BigQuery.

---

## ⚙️ Cómo correr el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/yogonet-scraper.git
cd yogonet-scraper
```

### 2 . Deployar el cloud run job
```bash
sh ./deploy.sh
```

### 3. Ejecutar el job
```bash
python callback.py
```
