import sqlite3

CARROS_INICIAIS = [
    # JAPONESES
    ("Honda Civic", 160),
    ("Mazda RX-7", 255),
    ("Nissan 350Z", 287),
    ("Mitsubishi Lancer Evo IX", 286),
    ("Subaru Impreza WRX STI", 300),
    ("Toyota Supra MK4", 320),
    ("Nissan Skyline GT-R R34", 280),

    # EUROPEUS
    ("Volkswagen Golf GTI", 220),
    ("BMW M3 E46", 343),
    ("Audi R8", 420),
    ("Porsche 911 Turbo", 420),
    ("Mercedes-Benz AMG GT", 469),

    # MUSCLE CARS
    ("Ford Mustang GT", 450),
    ("Chevrolet Camaro SS", 455),
    ("Dodge Challenger R/T", 375),
    ("Dodge Charger R/T", 375),

    # SUPERCARROS
    ("Chevrolet Corvette Z06", 505),
    ("Ford Mustang Shelby GT500", 760),
    ("Lamborghini Huracán", 610),

    # CLÁSSICOS DO BRASIL
    ("Chevrolet Opala", 140),
    ("Volkswagen Gol GTI", 120),
]

PECAS_INICIAIS = [
    # Indução Forçada & Sobrealimentação
    ("Kit Turbo Estágio 1 (.50)", 60, None),
    ("Kit Turbo Estágio 2 (.70)", 95, None),
    ("Turbo Estágio 3 Roletado", 140, None),
    ("Supercharger Twin-Screw", 110, None),
    ("Intercooler Frontal em Alumínio", 35, None),
    ("Válvula de Alívio Blow-Off", 10, None),

    # Admissão & Alimentação
    ("Filtro de Ar Cônico Esportivo", 12, None),
    ("Intake de Fibra de Carbono", 22, None),
    ("Bicos Injetores de Alta Vazão", 30, None),
    ("Bomba de Combustível Walbro 450", 18, None),
    ("Coletor de Admissão Plenum", 28, None),

    # Comando & Motor
    ("Comando de Válvulas Bravo 288°", 55, None),
    ("Pistões Forjados com Bielas em H", 75, None),
    ("Velas Iridium & Cabos Alta Volt.", 15, None),

    # Exaustão
    ("Coletor de Escape 4x1 em Inox", 25, None),
    ("Downpipe Inox de Alta Performance", 32, None),
    ("Escapamento Direto Full Inox 3 Pol", 40, None),

    # Eletrônica & Injeção Programável
    ("Remap de ECU Estágio 1", 35, None),
    ("Injeção Programável FuelTech FT550", 85, None),
    ("Two-Step com Launch Control", 15, None),

    # Boost Extra (Potência Bruta)
    ("Kit Nitro Shot 50 cv", 50, None),
    ("Kit Nitro Shot 100 cv", 100, None),
    ("Kit Nitro Shot 200 cv Direct Port", 200, None),
    ("Kit de Injeção Água/Metanol", 45, None),
]


def conectar():
    """Cria e configura uma conexão com suporte a chaves estrangeiras."""
    conn = sqlite3.connect("garagem_nfs.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_banco():
    """Cria o esquema relacional e popula os dados padrão caso não existam."""
    with conectar() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS carros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modelo TEXT UNIQUE NOT NULL,
                potencia_base INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pecas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                bonus_potencia INTEGER NOT NULL,
                carro_id INTEGER,
                FOREIGN KEY (carro_id) REFERENCES carros(id) ON DELETE SET NULL
            );
        """
        )

        conn.executemany(
            "INSERT OR IGNORE INTO carros (modelo, potencia_base) VALUES (?, ?);",
            CARROS_INICIAIS,
        )

        total_pecas = conn.execute("SELECT COUNT(*) FROM pecas;").fetchone()[0]
        if total_pecas == 0:
            conn.executemany(
                "INSERT INTO pecas (nome, bonus_potencia, carro_id) VALUES (?, ?, ?);",
                PECAS_INICIAIS,
            )


def obter_carros_com_potencia():
    """Retorna lista com cálculo dinâmico de potência total somando os bônus instalados."""
    query = """
        SELECT
            c.id,
            c.modelo,
            c.potencia_base,
            COALESCE(SUM(p.bonus_potencia), 0) AS total_bonus,
            c.potencia_base + COALESCE(SUM(p.bonus_potencia), 0) AS potencia_final
        FROM carros c
        LEFT JOIN pecas p ON c.id = p.carro_id
        GROUP BY c.id, c.modelo, c.potencia_base
        ORDER BY potencia_final DESC;
    """
    with conectar() as conn:
        return conn.execute(query).fetchall()


def obter_carro_por_id(carro_id):
    """Busca um veículo pelo ID."""
    with conectar() as conn:
        return conn.execute(
            "SELECT modelo, potencia_base FROM carros WHERE id = ?;", (carro_id,)
        ).fetchone()


def obter_pecas_do_carro(carro_id):
    """Retorna as peças atualmente instaladas em um veículo."""
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nome, bonus_potencia FROM pecas WHERE carro_id = ?;", (carro_id,)
        ).fetchall()


def obter_pecas_estoque():
    """Retorna todas as peças com carro_id IS NULL (disponíveis no estoque)."""
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nome, bonus_potencia FROM pecas WHERE carro_id IS NULL;"
        ).fetchall()


def vincular_peca(carro_id, peca_id):
    """Instala uma peça do estoque em um veículo."""
    with conectar() as conn:
        carro = conn.execute(
            "SELECT modelo FROM carros WHERE id = ?;", (carro_id,)
        ).fetchone()
        if not carro:
            return False, "Carro não encontrado."

        peca = conn.execute(
            "SELECT nome FROM pecas WHERE id = ? AND carro_id IS NULL;", (peca_id,)
        ).fetchone()
        if not peca:
            return False, "Peça inválida ou já instalada em outro veículo."

        conn.execute(
            "UPDATE pecas SET carro_id = ? WHERE id = ?;", (carro_id, peca_id)
        )
        return True, f"Peça '{peca[0]}' instalada com sucesso no {carro[0]}."


def desvincular_peca(carro_id, peca_id):
    """Remove uma peça instalada e devolve-a ao estoque."""
    with conectar() as conn:
        peca = conn.execute(
            "SELECT nome FROM pecas WHERE id = ? AND carro_id = ?;", (peca_id, carro_id)
        ).fetchone()
        if not peca:
            return False, "Peça não encontrada neste carro."

        conn.execute(
            "UPDATE pecas SET carro_id = NULL WHERE id = ?;", (peca_id,)
        )
        return True, f"Peça '{peca[0]}' desinstalada e devolvida ao estoque."