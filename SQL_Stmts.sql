CREATE TABLE accounts(
    acc_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    type VARCHAR(50),
    balance NUMERIC(10,2)
);

CREATE TABLE budgets(
    budget_id SERIAL PRIMARY KEY,
    category VARCHAR(50),
    limit_amount NUMERIC(10,2),
    spent NUMERIC(10,2)
);

CREATE TABLE transactions(
    trans_id SERIAL PRIMARY KEY,
    acc_id INT REFERENCES accounts(acc_id) ON DELETE CASCADE,
    type VARCHAR(50),
    amount NUMERIC(10,2),
    category VARCHAR(50),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);