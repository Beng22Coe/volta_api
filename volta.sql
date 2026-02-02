-- Volta Database Schema
-- =========================
-- users
-- =========================
CREATE TABLE users (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  full_name     VARCHAR(120)     NOT NULL,
  phone         VARCHAR(30)      NULL,
  email         VARCHAR(190)     NULL,
  role          ENUM('admin','moderator','driver') NOT NULL DEFAULT 'driver',
  password_hash VARCHAR(255)     NULL,
  status        ENUM('active','inactive','suspended') NOT NULL DEFAULT 'active',
  created_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email),
  UNIQUE KEY uq_users_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- nodes (stops/locations)
-- =========================
CREATE TABLE nodes (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name        VARCHAR(150)     NOT NULL,
  latitude    DECIMAL(10,7)    NOT NULL,
  longitude   DECIMAL(10,7)    NOT NULL,
  type        ENUM('station','terminal', 'landmark','junction') NOT NULL DEFAULT 'station',
  status ENUM('active','inactive') NOT NULL DEFAULT 'active',
  created_at  TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_nodes_lat_lng (latitude, longitude),
  KEY idx_nodes_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- routes
-- =========================
CREATE TABLE routes (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code        VARCHAR(50)      NULL,
  name        VARCHAR(150)     NOT NULL,
  created_by  BIGINT UNSIGNED  NULL,
  is_active   TINYINT(1)       NOT NULL DEFAULT 1,
  created_at  TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_routes_code (code),
  KEY idx_routes_created_by (created_by),
  CONSTRAINT fk_routes_created_by
    FOREIGN KEY (created_by) REFERENCES users(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- route_nodes (order of nodes within a route)
-- =========================
CREATE TABLE route_nodes (
  id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  route_id           BIGINT UNSIGNED NOT NULL,
  node_id            BIGINT UNSIGNED NOT NULL,
  seq_no             INT UNSIGNED    NOT NULL,  -- 1..N order in the route
  distance_km_from_start DECIMAL(10,3) NULL,
  travel_minutes_from_start INT UNSIGNED NULL,
  created_at         TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_route_nodes_route_seq (route_id, seq_no),
  UNIQUE KEY uq_route_nodes_route_node (route_id, node_id),
  KEY idx_route_nodes_node (node_id),
  CONSTRAINT fk_route_nodes_route
    FOREIGN KEY (route_id) REFERENCES routes(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_route_nodes_node
    FOREIGN KEY (node_id) REFERENCES nodes(id)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- vehicles
-- =========================
CREATE TABLE vehicles (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  plate_number VARCHAR(30)      NOT NULL,
  model        VARCHAR(80)      NULL,
  route_id     BIGINT UNSIGNED  NULL,      -- current assigned route (optional)
  driver_id    BIGINT UNSIGNED  NULL,      -- user with role=driver (optional)
  status       ENUM('active','inactive','suspended') NOT NULL DEFAULT 'active',
  created_at   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_vehicles_plate (plate_number),
  KEY idx_vehicles_route (route_id),
  KEY idx_vehicles_driver (driver_id),
  CONSTRAINT fk_vehicles_route
    FOREIGN KEY (route_id) REFERENCES routes(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_vehicles_driver
    FOREIGN KEY (driver_id) REFERENCES users(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- fares (pricing; route-based, optionally by segment)
-- =========================
CREATE TABLE fares (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  route_id      BIGINT UNSIGNED NOT NULL,
  from_node_id  BIGINT UNSIGNED NULL,
  to_node_id    BIGINT UNSIGNED NULL,
  amount        DECIMAL(10,2)   NOT NULL,
  currency      CHAR(3)         NOT NULL DEFAULT 'TZS',
  status        ENUM('active','inactive') NOT NULL DEFAULT 'active',
  created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_fares_route (route_id),
  KEY idx_fares_from_to (from_node_id, to_node_id),
  CONSTRAINT fk_fares_route
    FOREIGN KEY (route_id) REFERENCES routes(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_fares_from_node
    FOREIGN KEY (from_node_id) REFERENCES nodes(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT fk_fares_to_node
    FOREIGN KEY (to_node_id) REFERENCES nodes(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT chk_fares_amount_nonneg CHECK (amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
