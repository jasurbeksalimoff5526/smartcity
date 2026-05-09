CREATE TABLE users_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMPTZ NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE INDEX users_user_role_idx ON users_user(role);

CREATE TABLE incidents_category (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE incidents_incident (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    description TEXT NOT NULL,
    image VARCHAR(100) NOT NULL,
    latitude NUMERIC(9, 6) NULL,
    longitude NUMERIC(9, 6) NULL,
    address VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    resolution_note TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    category_id BIGINT NOT NULL,
    citizen_id BIGINT NOT NULL,
    technician_id BIGINT NULL,
    CONSTRAINT incidents_incident_category_fk
        FOREIGN KEY (category_id) REFERENCES incidents_category(id)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT incidents_incident_citizen_fk
        FOREIGN KEY (citizen_id) REFERENCES users_user(id)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT incidents_incident_technician_fk
        FOREIGN KEY (technician_id) REFERENCES users_user(id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX incident_status_idx ON incidents_incident(status);
CREATE INDEX incident_category_idx ON incidents_incident(category_id);
CREATE INDEX incident_priority_idx ON incidents_incident(priority);
CREATE INDEX incident_status_priority_idx ON incidents_incident(status, priority);
CREATE INDEX incidents_incident_citizen_id_idx ON incidents_incident(citizen_id);
CREATE INDEX incidents_incident_technician_id_idx ON incidents_incident(technician_id);

CREATE TABLE feedback_feedback (
    id BIGSERIAL PRIMARY KEY,
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    citizen_id BIGINT NOT NULL,
    incident_id BIGINT NOT NULL,
    CONSTRAINT feedback_feedback_citizen_fk
        FOREIGN KEY (citizen_id) REFERENCES users_user(id)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT feedback_feedback_incident_fk
        FOREIGN KEY (incident_id) REFERENCES incidents_incident(id)
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT unique_feedback_per_incident_citizen
        UNIQUE (incident_id, citizen_id)
);

CREATE INDEX feedback_feedback_citizen_id_idx ON feedback_feedback(citizen_id);
CREATE INDEX feedback_feedback_incident_id_idx ON feedback_feedback(incident_id);
