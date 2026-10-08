PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS upstream_repo (
    id INTEGER PRIMARY KEY,
    repo_key TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL UNIQUE,
    upstream_url TEXT NOT NULL,
    pinned_commit TEXT NOT NULL,
    role TEXT,
    status TEXT NOT NULL DEFAULT 'STUDY'
);

CREATE TABLE IF NOT EXISTS repo_dependency (
    id INTEGER PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    dependency_type TEXT NOT NULL,
    dependency_name TEXT NOT NULL,
    dependency_ref TEXT,
    FOREIGN KEY (repo_id) REFERENCES upstream_repo(id)
);

CREATE TABLE IF NOT EXISTS artifact (
    id INTEGER PRIMARY KEY,
    artifact_type TEXT NOT NULL,
    source_repo_id INTEGER,
    source_path TEXT,
    sha256 TEXT,
    metadata_json TEXT,
    FOREIGN KEY (source_repo_id) REFERENCES upstream_repo(id)
);

CREATE TABLE IF NOT EXISTS artifact_relation (
    id INTEGER PRIMARY KEY,
    from_artifact_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    to_artifact_id INTEGER NOT NULL,
    FOREIGN KEY (from_artifact_id) REFERENCES artifact(id),
    FOREIGN KEY (to_artifact_id) REFERENCES artifact(id)
);

CREATE TABLE IF NOT EXISTS experiment (
    id INTEGER PRIMARY KEY,
    experiment_key TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS experiment_run (
    id INTEGER PRIMARY KEY,
    experiment_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    input_json TEXT,
    output_json TEXT,
    FOREIGN KEY (experiment_id) REFERENCES experiment(id)
);

CREATE TABLE IF NOT EXISTS observation_mapping (
    id INTEGER PRIMARY KEY,
    source_system TEXT NOT NULL,
    source_field TEXT NOT NULL,
    target_system TEXT NOT NULL,
    target_field TEXT NOT NULL,
    notes TEXT,
    UNIQUE(source_system, source_field, target_system, target_field)
);
