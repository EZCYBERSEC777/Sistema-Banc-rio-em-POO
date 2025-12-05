import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

# =============================================================================
# 1. MODELAGEM (MANTIDA CONFORME UML)
# =============================================================================

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        # A transação só é registrada se o método depositar da conta retornar True
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        # Armazena um dicionário simples para o extrato, contendo o tipo da classe
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        # Polimorfismo: O cliente passa a conta e a transação (Saque ou Deposito)
        # Quem executa a lógica final é a própria transação.
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n❌ Operação falhou! Você não tem saldo suficiente.")
            return False
        elif valor > 0:
            self._saldo -= valor
            print("\n✅ Saque realizado com sucesso!")
            return True
        else:
            print("\n❌ Operação falhou! O valor informado é inválido.")
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n✅ Depósito realizado com sucesso!")
            return True
        else:
            print("\n❌ Operação falhou! O valor informado é inválido.")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        # Conta quantos saques já existem no histórico
        numero_saques = len(
            [t for t in self.historico.transacoes if t["tipo"] == "Saque"]
        )

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print(f"\n❌ Operação falhou! O valor do saque excede o limite de R$ {self.limite:.2f}.")
            return False

        elif excedeu_saques:
            print(f"\n❌ Operação falhou! Número máximo de saques diários excedido.")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


# =============================================================================
# 2. CONTROLLERS (MÉTODOS DE MENU ATUALIZADOS)
# =============================================================================

def menu():
    menu_text = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_text))


def filtrar_cliente(cpf, clientes):
    """Retorna a instância de PessoaFisica encontrada ou None."""
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    """
    Recupera a conta do cliente para operação.
    Se o cliente tiver mais de uma conta, aqui seria o local para deixá-lo escolher.
    Por enquanto, retorna a primeira conta disponível (índice 0).
    """
    if not cliente.contas:
        print("\n❌ Cliente não possui conta cadastrada!")
        return None
    
    # Retorna a primeira conta (Objeto ContaCorrente)
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌ Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    
    # Cria uma transação (Objeto)
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    # O Cliente inicia a transação passando a Conta alvo e o Objeto Transação
    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌ Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do saque: "))
    
    # Cria uma transação (Objeto)
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    # O Cliente inicia a transação
    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌ Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    # Acessa o histórico através da propriedade do objeto Conta
    transacoes = conta.historico.transacoes

    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for transacao in transacoes:
            print(f"\n{transacao['tipo']}:")
            print(f"\tR$ {transacao['valor']:.2f}")
            print(f"\tData: {transacao['data']}")

    print(f"\nSaldo atual:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n❌ Já existe cliente com esse CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    # Instancia o objeto PessoaFisica e salva na lista
    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    print("\n✅ Cliente criado com sucesso!")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❌ Cliente não encontrado. Fluxo encerrado.")
        return

    # Factory method para criar a instância de ContaCorrente
    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    
    # Vincula a conta às listas de controle e ao próprio objeto Cliente
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n✅ Conta criada com sucesso!")


def listar_contas(contas):
    # Itera sobre lista de objetos ContaCorrente e usa o método __str__ de cada um
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


# =============================================================================
# 3. BLOCO PRINCIPAL
# =============================================================================

def main():
    # Listas para armazenar as instâncias dos objetos em memória
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("\n👋 Saindo do sistema...")
            break

        else:
            print("\n❌ Operação inválida, por favor selecione novamente.")


if __name__ == "__main__":
    main()
