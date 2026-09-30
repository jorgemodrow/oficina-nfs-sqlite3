def linha(tamanho=55):
    """Retorna uma linha separadora."""
    return "-" * tamanho


def cabecalho(texto, tamanho=55):
    """Exibe um cabeçalho centralizado."""
    print("=" * tamanho)
    print(texto.center(tamanho))
    print("=" * tamanho)


def leia_int(msg):
    """Solicita ao usuário um número inteiro válido."""
    while True:
        try:
            return int(input(msg).strip())
        except (ValueError, TypeError):
            print("\033[31mERRO: digite um número inteiro válido.\033[m")
        except KeyboardInterrupt:
            print("\n\033[31mEntrada cancelada pelo usuário.\033[m")
            return 0


def msg_sucesso(texto):
    """Exibe uma mensagem de sucesso em verde."""
    print(f"\033[32m{texto}\033[m")


def msg_erro(texto):
    """Exibe uma mensagem de erro em vermelho."""
    print(f"\033[31m{texto}\033[m")


def msg_alerta(texto):
    """Exibe uma mensagem de alerta em amarelo."""
    print(f"\033[33m{texto}\033[m")