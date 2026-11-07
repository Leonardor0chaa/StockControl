
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from dotenv import load_dotenv
from decimal import Decimal, InvalidOperation
import mysql.connector
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave-local-desenvolvimento")

def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route("/")
def inicio():
    return redirect(url_for("produtos"))

@app.route("/produtos", methods=["GET", "POST"])
def produtos():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco_texto = request.form.get("preco", "").strip()
        categoria_texto = request.form.get("categoria_id", "")
        quantidade_texto = request.form.get("quantidadeEstoque", "")
        minimo_texto = request.form.get("estoqueMinimo", "")

        try:
            preco = Decimal(preco_texto.replace(",", "."))
            categoria_id = int(categoria_texto)
            quantidade = int(quantidade_texto)
            minimo = int(minimo_texto)

            if not nome or len(nome) > 100:
                raise ValueError("Informe um nome válido.")

            if preco <= 0 or not preco.is_finite():
                raise ValueError("O preço deve ser maior que zero.")

            if preco > Decimal("99999999.99"):
                raise ValueError("O preço informado é muito alto.")

            if quantidade < 0 or minimo < 0:
                raise ValueError("As quantidades não podem ser negativas.")

            if categoria_id <= 0:
                raise ValueError("Selecione uma categoria.")

        except (ValueError, InvalidOperation):
            flash("Verifique os campos do formulário.", "erro")
            return redirect(url_for("produtos"))

        conexao = None

        try:
            conexao = conectar_banco()
            cursor = conexao.cursor()

            sql = """
                INSERT INTO PRODUTO
                (nome, descricao, preco, quantidadeEstoque,
                 estoqueMinimo, categoria_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                nome, descricao, preco, quantidade,
                minimo, categoria_id
            ))

            conexao.commit()
            cursor.close()

            flash("Produto cadastrado com sucesso!", "sucesso")

        except mysql.connector.Error:
            if conexao is not None:
                conexao.rollback()
            app.logger.exception("Erro ao cadastrar produto")
            flash("Não foi possível cadastrar o produto.", "erro")

        finally:
            if conexao is not None and conexao.is_connected():
                conexao.close()

        return redirect(url_for("produtos"))

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, nome FROM CATEGORIA ORDER BY nome")
        categorias = cursor.fetchall()

        cursor.execute("""
            SELECT p.id, p.nome, p.preco,
                   p.quantidadeEstoque, p.estoqueMinimo,
                   c.nome AS categoria
            FROM PRODUTO p
            JOIN CATEGORIA c ON p.categoria_id = c.id
            ORDER BY p.id DESC
        """)
        lista_produtos = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "produtos.html",
        categorias=categorias,
        produtos=lista_produtos
    )


@app.route("/movimentacoes", methods=["GET", "POST"])
def movimentacoes():
    if request.method == "POST":
        produto_texto = request.form.get("produto_id", "")
        tipo = request.form.get("tipo", "")
        quantidade_texto = request.form.get("quantidade", "")
        observacao = request.form.get("observacao", "").strip()

        try:
            produto_id = int(produto_texto)
            quantidade = int(quantidade_texto)

            if produto_id <= 0 or quantidade <= 0:
                raise ValueError()

            if tipo not in ("ENTRADA", "SAIDA"):
                raise ValueError()

            if len(observacao) > 255:
                raise ValueError()

        except ValueError:
            flash("Verifique os dados da movimentação.", "erro")
            return redirect(url_for("movimentacoes"))

        conexao = None
        cursor = None

        try:
            conexao = conectar_banco()
            conexao.start_transaction()
            cursor = conexao.cursor(dictionary=True)

            # Bloqueia o produto durante a atualização.
            cursor.execute(
                """
                SELECT id, nome, quantidadeEstoque
                FROM PRODUTO
                WHERE id = %s
                FOR UPDATE
                """,
                (produto_id,)
            )

            produto = cursor.fetchone()

            if produto is None:
                raise ValueError("Produto não encontrado.")

            estoque_atual = produto["quantidadeEstoque"]

            if tipo == "SAIDA" and quantidade > estoque_atual:
                raise ValueError(
                    f"Estoque insuficiente! Disponível: {estoque_atual} unidades."
                )

            if tipo == "ENTRADA":
                novo_estoque = estoque_atual + quantidade
            else:
                novo_estoque = estoque_atual - quantidade

            cursor.execute(
                """
                SELECT id FROM USUARIO
                WHERE email = %s
                LIMIT 1
                """,
                ("admin@stockcontrol.local",)
            )

            usuario = cursor.fetchone()

            if usuario is None:
                raise ValueError("Administrador de teste não encontrado.")

            cursor.execute(
                """
                UPDATE PRODUTO
                SET quantidadeEstoque = %s
                WHERE id = %s
                """,
                (novo_estoque, produto_id)
            )

            cursor.execute(
                """
                INSERT INTO MOVIMENTACAO_ESTOQUE
                (tipo, quantidade, data, observacao, produto_id, usuario_id)
                VALUES (%s, %s, NOW(), %s, %s, %s)
                """,
                (
                    tipo,
                    quantidade,
                    observacao,
                    produto_id,
                    usuario["id"]
                )
            )

            conexao.commit()

            flash(
                f"Movimentação registrada! Novo estoque: {novo_estoque} unidades.",
                "sucesso"
            )

        except ValueError as erro:
            if conexao is not None:
                conexao.rollback()
            flash(str(erro), "erro")

        except mysql.connector.Error:
            if conexao is not None:
                conexao.rollback()
            app.logger.exception("Erro ao registrar movimentação")
            flash("Erro ao registrar movimentação no banco.", "erro")

        finally:
            if cursor is not None:
                cursor.close()
            if conexao is not None and conexao.is_connected():
                conexao.close()

        return redirect(url_for("movimentacoes"))

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, nome, quantidadeEstoque
            FROM PRODUTO
            ORDER BY nome
        """)
        produtos = cursor.fetchall()

        cursor.execute("""
            SELECT m.id, m.data, m.tipo, m.quantidade,
                   m.observacao, p.nome AS produto,
                   u.nome AS responsavel
            FROM MOVIMENTACAO_ESTOQUE m
            JOIN PRODUTO p ON m.produto_id = p.id
            JOIN USUARIO u ON m.usuario_id = u.id
            ORDER BY m.data DESC, m.id DESC
        """)
        historico = cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()

    return render_template(
        "movimentacoes.html",
        produtos=produtos,
        historico=historico
    )


if __name__ == "__main__":
    app.run(debug=True)
