import psycopg2

def connect_db():
    conn = psycopg2.connect(
        host="awsprddbs4836.shared.sydney.edu.au",
        database="y26s1c9120_uban0722",
        user="y26s1c9120_uban0722",
        password="Poloclub@123"
    )
    return conn