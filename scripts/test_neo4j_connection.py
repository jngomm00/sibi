from neo4j import GraphDatabase

# Configura los datos de tu conexión
uri = "neo4j://127.0.0.1:7687"
user = "neo4j"
password = "j7hm3HtMmuj3g75"

driver = GraphDatabase.driver(uri, auth=(user, password))

def test_connection():
    try:
        with driver.session(database="neo4j") as session:
            result = session.run("RETURN 'Conexión exitosa con Neo4j' AS message")
            for record in result:
                print(record["message"])
    except Exception as e:
        print("Error al conectar:", e)

if __name__ == "__main__":
    test_connection()
