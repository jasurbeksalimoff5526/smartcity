# Smart City Incident Management System

Django MVT asosidagi Smart City incident boshqaruv tizimi. Fuqarolar shahar infratuzilmasidagi muammolarni foto, location, category va priority bilan yuboradi. Operator incidentni technician ga biriktiradi, technician resolution yozadi, citizen esa feedback qoldirib incidentni yopadi.

## Stack

- Python
- Django
- PostgreSQL
- Django Templates
- Bootstrap

## Rolelar

- Citizen: incident yaratadi, o'z incidentlarini kuzatadi, resolved incidentga feedback beradi.
- Operator: barcha incidentlarni ko'radi, technician ga assign qiladi, status va priority ni boshqaradi.
- Technician: o'ziga biriktirilgan incidentlarni ko'radi, resolution note yozadi va statusni `RESOLVED` qiladi.
- Admin: user/category/admin panel/dashboard monitoringini boshqaradi.

## Incident Flow

`NEW -> IN_PROGRESS -> RESOLVED -> CLOSED`

1. Citizen incident yaratadi.
2. Operator incidentni ko'radi.
3. Operator technician ga assign qiladi.
4. Technician muammoni hal qilib resolution yozadi.
5. Status `RESOLVED` bo'ladi.
6. Citizen feedback beradi yoki incidentni yopadi.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

PostgreSQL database yarating:

```sql
CREATE DATABASE smart_city_db;
```

`.env` yoki shell orqali kerakli qiymatlarni bering:

```bash
set POSTGRES_DB=smart_city_db
set POSTGRES_USER=postgres
set POSTGRES_PASSWORD=password
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5432
```

Migratsiya va server:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## PostgreSQL Schema

SQL topshirig'i uchun schema fayli:

- `docs/database_schema.sql`
- `docs/drawsql.md`

Foreign keylar va recommended indexlar (`status`, `category_id`, `priority`) SQL faylda ham, Django model `Meta.indexes` ichida ham berilgan.

## App Structure

```text
SmartCity/
├── conf/
├── users/
├── incidents/
├── feedback/
├── dashboard/
├── templates/
├── static/
├── media/
├── docs/
├── manage.py
└── requirements.txt
```

## Git Strategy

Tavsiya qilingan branchlar:

- `main`
- `develop`
- `feature/auth-system`
- `feature/incidents`
- `feature/dashboard`
