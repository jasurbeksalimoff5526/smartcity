# DrawSQL import guide

Use `docs/database_schema.sql` as the PostgreSQL source for DrawSQL.

Core tables:

- `users_user`
- `incidents_category`
- `incidents_incident`
- `feedback_feedback`

Main relations:

- `incidents_incident.citizen_id -> users_user.id`
- `incidents_incident.technician_id -> users_user.id`
- `incidents_incident.category_id -> incidents_category.id`
- `feedback_feedback.incident_id -> incidents_incident.id`
- `feedback_feedback.citizen_id -> users_user.id`

Recommended indexes are included for `status`, `category_id`, and `priority`.
