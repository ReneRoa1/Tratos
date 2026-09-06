class SessaoUsuario:

    def __init__(self):
        self.limpar()

    def limpar(self):

        self.usuario_id = None
        self.nome = None
        self.login = None
        self.perfil_sistema = None

        self.organizacoes = []
        self.fazendas = []

        self.fazenda_atual_id = None
        self.fazenda_atual_nome = None
        self.fazenda_atual_perfil = None

    def selecionar_fazenda(
        self,
        fazenda_id,
        fazenda_nome,
        perfil=None
    ):

        self.fazenda_atual_id = fazenda_id
        self.fazenda_atual_nome = fazenda_nome
        self.fazenda_atual_perfil = perfil


sessao = SessaoUsuario()