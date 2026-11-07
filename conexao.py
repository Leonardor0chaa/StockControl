
import mysql.connector
from getpass import getpass

print("Conectando ao banco StockControl...")

senha = getpass("Digite a senha do MySQL: ")

try:
    conexao = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="stockcontrol_app",
    password=senha,
    database="stockcontrol"
    )

    if conexao.is_connected():
        print("Conexão com MySQL realizada com sucesso!")

        cursor = conexao.cursor()
        cursor.execute("SHOW TABLES")

        print("\nTabelas encontradas:")

        for tabela in cursor.fetchall():
            print("-", tabela[0])

        cursor.close()
        conexao.close()

except mysql.connector.Error as erro:
    print("Erro ao conectar ao MySQL:")
    print(erro)
