import database as db
import interface as ui


def pausa():
    """Pausa a execução até o pressionamento de Enter."""
    input("\nPressione <Enter> para voltar ao menu...")


def exibir_garagem(pausar=True):
    """Exibe todos os carros e suas respectivas potências em tabela alinhada."""
    ui.cabecalho("GARAGEM DE VEÍCULOS")
    carros = db.obter_carros_com_potencia()

    print(f"{'ID':<4} {'MODELO':<26} {'BASE':<8} {'BÔNUS':<8} {'TOTAL':<8}")
    print(ui.linha())
    for cid, mod, base, bonus, total in carros:
        print(f"{cid:<4} {mod:<26} {base:<8} +{bonus:<7} {total} cv")
    print(ui.linha())

    if pausar:
        pausa()


def exibir_detalhes():
    """Exibe a ficha técnica e as peças montadas em determinado carro."""
    carro_id = ui.leia_int("Informe o ID do carro: ")
    carro = db.obter_carro_por_id(carro_id)

    if not carro:
        ui.msg_erro("Carro não encontrado!")
        pausa()
        return

    modelo, base = carro
    pecas = db.obter_pecas_do_carro(carro_id)

    ui.cabecalho(f"FICHA TÉCNICA: {modelo}")
    print(f"Potência de Fábrica: {base} cv\n")

    if not pecas:
        ui.msg_alerta("Nenhuma peça de performance instalada neste veículo.")
        print(ui.linha())
    else:
        print(f"{'ID':<4} {'PEÇA INSTALADA':<35} {'BÔNUS':<10}")
        print(ui.linha())
        for pid, nome, bonus in pecas:
            print(f"{pid:<4} {nome:<35} +{bonus} cv")
        print(ui.linha())

    pausa()


def exibir_estoque(pausar=True):
    """Exibe a listagem tabular das peças disponíveis no estoque."""
    ui.cabecalho("ESTOQUE DE PEÇAS DISPONÍVEIS")
    pecas = db.obter_pecas_estoque()

    if not pecas:
        ui.msg_alerta("O estoque está vazio no momento.")
        print(ui.linha())
        if pausar:
            pausa()
        return False

    print(f"{'ID':<4} {'PEÇA':<35} {'BÔNUS':<10}")
    print(ui.linha())
    for pid, nome, bonus in pecas:
        print(f"{pid:<4} {nome:<35} +{bonus} cv")
    print(ui.linha())

    if pausar:
        pausa()
    return True


def acao_instalar():
    """Coordena o fluxo de montagem de um componente em um veículo."""
    exibir_garagem(pausar=False)
    carro_id = ui.leia_int("ID do carro que receberá o upgrade: ")

    if not db.obter_carro_por_id(carro_id):
        ui.msg_erro("Carro não cadastrado.")
        pausa()
        return

    tem_estoque = exibir_estoque(pausar=False)
    if not tem_estoque:
        pausa()
        return

    peca_id = ui.leia_int("ID da peça a instalar: ")
    sucesso, mensagem = db.vincular_peca(carro_id, peca_id)

    if sucesso:
        ui.msg_sucesso(mensagem)
    else:
        ui.msg_erro(mensagem)

    pausa()


def acao_desinstalar():
    """Coordena o desmonte de um componente de volta para o estoque."""
    carro_id = ui.leia_int("ID do carro para remoção de peça: ")
    carro = db.obter_carro_por_id(carro_id)

    if not carro:
        ui.msg_erro("Carro não cadastrado.")
        pausa()
        return

    pecas = db.obter_pecas_do_carro(carro_id)
    if not pecas:
        ui.msg_alerta("Este veículo não possui peças para desinstalar.")
        pausa()
        return

    ui.cabecalho(f"PEÇAS INSTALADAS EM: {carro[0]}")
    print(f"{'ID':<4} {'PEÇA':<35} {'BÔNUS':<10}")
    print(ui.linha())
    for pid, nome, bonus in pecas:
        print(f"{pid:<4} {nome:<35} +{bonus} cv")
    print(ui.linha())

    peca_id = ui.leia_int("ID da peça a remover: ")
    sucesso, mensagem = db.desvincular_peca(carro_id, peca_id)

    if sucesso:
        ui.msg_sucesso(mensagem)
    else:
        ui.msg_erro(mensagem)

    pausa()


def exibir_menu():
    """Renderiza visualmente as opções da oficina."""
    ui.cabecalho("SISTEMA DE TUNING & PERFORMANCE")
    print("1 - Listar Garagem (Potência Total)")
    print("2 - Ver Detalhes do Carro")
    print("3 - Listar Estoque de Peças")
    print("4 - Instalar Peça")
    print("5 - Desinstalar Peça")
    print("6 - Sair")
    print(ui.linha())


def menu():
    """Executa o laço interativo do menu principal."""
    db.inicializar_banco()

    opcoes = {
        1: exibir_garagem,
        2: exibir_detalhes,
        3: exibir_estoque,
        4: acao_instalar,
        5: acao_desinstalar,
    }

    while True:
        exibir_menu()
        opcao = ui.leia_int("Sua opção: ")

        if opcao == 6:
            ui.msg_alerta("Encerrando a oficina...")
            break

        acao = opcoes.get(opcao)
        if acao:
            acao()
        else:
            ui.msg_erro("Opção inválida! Escolha entre 1 e 6.")
            pausa()


if __name__ == "__main__":
    menu()