import psycopg2
import bcrypt
import re
import random
import string

# Declaração inicial das variáveis
connection = None
cursor = None

def conectar_banco():
    global connection, cursor
    connection = psycopg2.connect("dbname=py_Registro_dos_usuarios user=postgres password=123456")
    cursor = connection.cursor()

# cursor.execute("insert into usuarios (id, login, senha_hash, nome, email) values (id, login, senha, nome, email)")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

def gerar_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def menu_principal(logado):
    print("RPG Curricular")
    print("1. Login")
    print("2. Registrar")
    if logado:
        print("3. Atualizar Cadastro")
    print("4. Sair")


def realizar_login():
    usuario = input("Digite seu Login: ")
    senha = input("Digite sua senha: ")

    # Verificar as credenciais
    if verificar_usuario_valido():
        # Buscar senha hash do banco de dados
        cursor.execute("SELECT senha_hash FROM usuarios WHERE login = %s", (usuario,))
        senha_hash = cursor.fetchone()

        if senha_hash and bcrypt.checkpw(senha.encode(), senha_hash[0].encode()):  # Corrigido aqui
            print("Seja bem-vindo, {}!".format(usuario))
            return usuario  # Retorna o nome do usuário logado

    print("Login ou Senha inválidos. Tente novamente")
    return None  # Retorna None se o login falhar


def verificar_usuario_valido():
    # Pelo menos 3 letras
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]

    if count < 3:
        print("O usuario deve ter ao menos 3 letras")
        return False

    return True


def verificar_senha_valida(senha):
    # Pelo menos 6 caracteres
    if len(senha) < 6:
        return False

    # Pelo menos 1 caractere especial
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", senha):
        return False

    # Pelo menos 1 número
    if not re.search("[0-9]", senha):
        return False

    # Pelo menos 1 letra maiúscula
    if not re.search("[A-Z]", senha):
        return False

    return True


def verificar_email_valido(email):
    # Usando uma expressão regular simples para validar o formato do e-mail
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def registro():
    criar_usuario = input("Crie um login: ")

    # Verificar se o usuário já existe
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE login = %s", (criar_usuario,))
    count = cursor.fetchone()[0]

    if count > 0:
        print("Usuário já existe. Escolha outro nome de usuário.")
        return

    # Verificar se o usuário tem pelo menos 3 letras
    if len(criar_usuario) < 3:
        print("O usuário deve ter pelo menos 3 letras.")
        return

    while True:
        criar_senha = input("Crie uma senha: ")
        confirmar_senha = input("Confirme a senha: ")

        # Verificar se as senhas coincidem
        if criar_senha == confirmar_senha:
            # Verificar se a senha atende aos critérios
            if verificar_senha_valida(criar_senha):
                break
            else:
                print("A senha deve ter pelo menos 6 caracteres, 1 caractere especial, 1 número e 1 letra maiúscula.")
        else:
            print("As senhas não coincidem. Tente novamente.")

    while True:
        criar_email = input("Digite seu email: ")

        # Verificar se o e-mail tem um formato válido
        if verificar_email_valido(criar_email):
            break
        else:
            print("Formato de e-mail inválido. Tente novamente.")

    # Comando SQL sem mencionar a coluna 'id'
    cursor.execute("INSERT INTO usuarios (login, senha_hash, nome, email) VALUES (%s, %s, %s, %s)",
                   (criar_usuario, bcrypt.hashpw(criar_senha.encode(), bcrypt.gensalt()), "", criar_email))
    # Commit para salvar as alterações
    connection.commit()

    print("Usuário registrado com sucesso!")


def atualizar_cadastro(usuario):
    print("Atualizando cadastro para o usuário {}:".format(usuario))
    while True:
        nova_senha = input("Digite uma nova senha (ou pressione Enter para manter a mesma): ")
        if nova_senha == "":
            break
        confirmar_senha = input("Confirme a nova senha: ")
        if nova_senha == confirmar_senha:
            if verificar_senha_valida(nova_senha):
                cursor.execute("UPDATE usuarios SET senha_hash = %s WHERE login = %s",
                               (bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()), usuario))
                print("Senha atualizada com sucesso!")
                # Commit para salvar as alterações
                connection.commit()
                break
            else:
                print("A nova senha não atende aos critérios. Tente novamente.")
        else:
            print("As senhas não coincidem. Tente novamente.")

    novo_email = input("Digite um novo e-mail (ou pressione Enter para manter o mesmo): ")
    if novo_email != "":
        while not verificar_email_valido(novo_email):
            print("Formato de e-mail inválido. Tente novamente.")
            novo_email = input("Digite um novo e-mail (ou pressione Enter para manter o mesmo): ")
        cursor.execute("UPDATE usuarios SET email = %s WHERE login = %s", (novo_email, usuario))
        print("E-mail atualizado com sucesso!")

    novo_nome = input("Digite um novo nome (ou pressione Enter para manter o mesmo): ")
    if novo_nome != "":
        cursor.execute("UPDATE usuarios SET nome = %s WHERE login = %s", (novo_nome, usuario))
        print("Nome atualizado com sucesso!")


def main():
    global cursor
    conectar_banco()
    usuario_logado = None

    while True:
        menu_principal(usuario_logado is not None)
        escolha = input("Escolha a opção: ")

        if escolha == "1":
            usuario_logado = realizar_login()
        elif escolha == "2":
            registro()
        elif escolha == "3" and usuario_logado is not None:
            atualizar_cadastro(usuario_logado)
        elif escolha == "4":
            print("Até mais!")
            break
        else:
            print("Opção inválida. Por favor, escolha novamente.")


if __name__ == "__main__":
    main()
