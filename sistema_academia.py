from datetime import date, timedelta

# ============================================================
#  BUG PROPOSITAL — mude para True para a demonstração do bug
BUG_ATIVO = False
# ============================================================

PLANOS = {
    "mensal":      {"duracao": 30,  "valor": 99.90},
    "trimestral":  {"duracao": 90,  "valor": 269.90},
    "anual":       {"duracao": 365, "valor": 899.90},
}


class Membro:
    def __init__(self, nome, cpf, idade, plano):
        self.nome = nome
        self.cpf = cpf
        self.idade = int(idade)
        self.plano = plano
        self.ativo = True
        self.data_inicio = date.today()
        self.data_vencimento = date.today() + timedelta(days=PLANOS[plano]["duracao"])

    def to_dict(self):
        return {
            "nome": self.nome,
            "cpf": self.cpf,
            "idade": self.idade,
            "plano": self.plano,
            "ativo": self.ativo,
            "data_inicio": str(self.data_inicio),
            "data_vencimento": str(self.data_vencimento),
            "valor_plano": PLANOS[self.plano]["valor"],
        }


class SistemaAcademia:
    def __init__(self):
        self.membros = {}

    # RF01 - Cadastro de membros
    def cadastrar_membro(self, nome, cpf, idade, plano):
        if cpf in self.membros:
            raise ValueError("CPF já cadastrado no sistema")
        if int(idade) < 16:
            raise ValueError("Idade mínima para cadastro é 16 anos")
        if plano not in PLANOS:
            raise ValueError(f"Plano inválido. Opções: {', '.join(PLANOS)}")
        self.membros[cpf] = Membro(nome, cpf, int(idade), plano)
        return self.membros[cpf]

    # RF02 - Check-in
    def fazer_checkin(self, cpf):
        if cpf not in self.membros:
            raise ValueError("Membro não encontrado no sistema")
        membro = self.membros[cpf]

        # BUG: quando BUG_ATIVO eh True, ignora verificação de matrícula cancelada
        if not BUG_ATIVO:
            if not membro.ativo:
                raise ValueError("Matrícula cancelada. Renove para realizar check-in")

        if date.today() > membro.data_vencimento:
            raise ValueError("Matrícula vencida. Renove seu plano para check-in")
        return True

    # RF03 - Cancelamento de matrícula
    def cancelar_matricula(self, cpf):
        if cpf not in self.membros:
            raise ValueError("Membro não encontrado no sistema")
        self.membros[cpf].ativo = False
        return True

    # RF04 - Renovação de plano
    def renovar_plano(self, cpf, novo_plano):
        if cpf not in self.membros:
            raise ValueError("Membro não encontrado no sistema")
        if novo_plano not in PLANOS:
            raise ValueError(f"Plano inválido. Opções: {', '.join(PLANOS)}")
        membro = self.membros[cpf]
        membro.plano = novo_plano
        membro.data_vencimento = date.today() + timedelta(days=PLANOS[novo_plano]["duracao"])
        membro.ativo = True
        return membro

    def consultar_membro(self, cpf):
        if cpf not in self.membros:
            raise ValueError("Membro não encontrado no sistema")
        return self.membros[cpf]

    def listar_membros(self):
        return [m.to_dict() for m in self.membros.values()]

    def resetar(self):
        self.membros = {}
