--DROP DATABASE cookbook;

-- Create dataset
CREATE DATABASE IF NOT EXISTS cookbook;
USE cookbook;

-- Create users table
CREATE TABLE users (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    gender ENUM('male', 'female', 'other', 'non-binary') NOT NULL,
    age INT NOT NULL,
    height FLOAT NOT NULL,
    currentweight FLOAT NOT NULL,
    goalweight FLOAT NOT NULL,
    weightgoal ENUM('lose', 'gain', 'maintain') NOT NULL,
    nutritiongoal ENUM('regular', 'body_builder', 'weight_gain') NOT NULL,
    period INT NOT NULL
);

-- Create food table
CREATE TABLE food (
    foodid INT AUTO_INCREMENT PRIMARY KEY,
    foodname VARCHAR(255) NOT NULL,
    calories FLOAT NOT NULL
);

-- Create food_type table
CREATE TABLE food_type (
    typeid INT AUTO_INCREMENT PRIMARY KEY,
    foodid INT NOT NULL,
    typename ENUM('carbohydrate', 'protein', 'fat') NOT NULL,
    percentage INT NOT NULL,
    category VARCHAR(255),
    FOREIGN KEY (foodid) REFERENCES food(foodid) ON DELETE CASCADE
);

-- Create user_customize table
CREATE TABLE user_customize (
    userid INT NOT NULL,
    foodid INT NOT NULL,
    type ENUM('allergy', 'like', 'dislike') NOT NULL,
    PRIMARY KEY (userid, foodid),
    FOREIGN KEY (userid) REFERENCES users(userid) ON DELETE CASCADE,
    FOREIGN KEY (foodid) REFERENCES food(foodid) ON DELETE CASCADE
);
