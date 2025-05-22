
# 📚 Library Management System

A basic Flask-based Library Management System with PostgreSQL integration. Run it manually or via Docker Compose for ease.

---

## 🚀 Getting Started

### 1. Clone the Repository

Make sure Git is installed.

```bash
git clone https://github.com/clumsyspeedboat/library_management_task.git
cd library_management_task
```

---

## ⚙️ Running Without Docker

### 2. Set Up Python Virtual Environment

Ensure Python is installed and available in your PATH.

```bash
python -m venv env
```

### 3. Activate the Virtual Environment

- **Windows:**
  ```bash
  env\Scripts\activate
  ```
- **Linux/Mac:**
  ```bash
  source env/bin/activate
  ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Flask App

```bash
python app.py
```

### 6. Open the Application

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🐳 Running With Docker (Recommended)

### 1. Start the App Using Docker Compose

```bash
docker-compose up --build
```

This will:
- Start the Flask app on `http://localhost:5000`
- Start PostgreSQL on `localhost:5432`
- Load schema and sample data on first run

---

## 🐘 PostgreSQL Database Info

| Setting   | Value    |
|-----------|----------|
| Host      | db       |
| Port      | 5432     |
| Database  | library  |
| Username  | lms      |
| Password  | lms123   |

> Initial schema and data are loaded from:
> - `01-schema.sql`
> - `02-data.sql`

---

## 🔁 Resetting the Database

To reset the database and re-apply schema and data:

```bash
docker-compose down -v
docker-compose up --build
```

---

## 🔍 Accessing the Database Manually

Enter the PostgreSQL container:

```bash
docker exec -it library_management_task-db-1 psql -U lms -d library
```

Inside `psql`, list tables with:

```sql
\dt
```

---
