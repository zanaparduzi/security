CREATE DATABASE Users;
USE Users;
CREATE TABLE Utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(50),
    surname VARCHAR(50),
    password VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20)
);
ALTER TABLE Utilisateurs ADD COLUMN admin INT NOT NULL DEFAULT 0 CHECK (admin >= 0 AND admin <= 2);
UPDATE Utilisateurs SET admin = 0;
INSERT INTO Utilisateurs (username, name, surname, password, email, phone_number, admin)
VALUES ('admin++', 'admin ++', 'admin++', 'admin', 'admin@gmail.com', '01', 2);
