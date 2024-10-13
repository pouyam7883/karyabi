CREATE DATABASE IF NOT EXISTS karjoo
    CHARACTER SET utf8
    COLLATE utf8_general_ci;

USE karjoo;

CREATE USER 'karjoo_admin'@'localhost' IDENTIFIED BY 'karjoo_password';

GRANT ALL PRIVILEGES ON *.* TO 'karjoo_admin'@'localhost';

CREATE TABLE register (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(15) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    father_name VARCHAR(50) NOT NULL,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    email VARCHAR(100),
    birth_place VARCHAR(50),
    birth_date DATE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Personal_Info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    gender VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    father_name VARCHAR(50) NOT NULL,
    birth_date DATE NOT NULL,
    birth_place VARCHAR(50),
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Identification_Info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    email VARCHAR(100),
    birth_certificate_number VARCHAR(50),
    issuance_place VARCHAR(50),
    religion VARCHAR(50),
    nationality VARCHAR(50),
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Marital_Health_Status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    marital_status VARCHAR(50) NOT NULL,
    children_count INT DEFAULT 0,
    health_status VARCHAR(50) NOT NULL,
    health_details TEXT,
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Education (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    last_degree VARCHAR(50),
    field_of_study VARCHAR(100),
    gpa DECIMAL(4, 2),
    graduation_date DATE,
    university_type VARCHAR(50),
    institute_name VARCHAR(100),
    city_country VARCHAR(100),
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Work_Experience (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    organization_name VARCHAR(100),
    job_title VARCHAR(100),
    contact_number VARCHAR(15),
    start_date DATE,
    end_date DATE,
    last_salary DECIMAL(10, 2),
    reason_for_leaving TEXT,
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Language_Computer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    reading VARCHAR(50),
    writing VARCHAR(50),
    speaking VARCHAR(50),
    computer_skills TEXT,
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Specialty_Certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    specialty_name VARCHAR(100),
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Work_Preference (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    work_preference TEXT,
    other_details TEXT,
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Insurance_Status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    insurance_status VARCHAR(50) NOT NULL,
    insurance_details TEXT,
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Guarantors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    relationship VARCHAR(50),
    job VARCHAR(100),
    address TEXT,
    phone VARCHAR(15),
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Work_Area (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    work_area VARCHAR(100),
    preferred_city VARCHAR(50),
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);

CREATE TABLE Military_Service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    national_code VARCHAR(10) NOT NULL UNIQUE,
    service_status VARCHAR(50) NOT NULL,
    exemption_details TEXT,
    FOREIGN KEY (national_code) REFERENCES register(national_code)
);
