Expense Tracker App

This is a simple expense tracker web application built using FastAPI and MySQL. It allows users to register, log in, and manage their daily expenses.

Features

- User registration and login
- Add, edit, and delete expenses
- View all expenses
- Category-wise expense tracking
- Monthly summary
- Download expenses as CSV

Tech Stack

- Backend: FastAPI
- Database: MySQL
- Frontend: HTML, CSS (Jinja2 templates)

Setup Instructions

1. Clone the repository

git clone https://github.com/SubhGit17/expense-tracker.git
cd expense-tracker

2. Create virtual environment

python -m venv venv
venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Create .env file

Create a file named ".env" in the root folder and add:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=expense_tracker
DB_PORT=3306

5. Setup MySQL database

Run the following queries in MySQL:

CREATE DATABASE expense_tracker;
USE expense_tracker;

CREATE TABLE users (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100) UNIQUE,
password VARCHAR(255)
);

CREATE TABLE expenses (
id INT AUTO_INCREMENT PRIMARY KEY,
title VARCHAR(100),
amount DECIMAL(10,2),
category VARCHAR(50),
date DATE,
user_id INT
);

6. Run the application

uvicorn main:app --reload

Open in browser:
http://127.0.0.1:8000

Notes

- The .env file is not uploaded to GitHub for security reasons
- Make sure MySQL is running on your system