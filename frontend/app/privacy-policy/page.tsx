export const dynamic = 'force-dynamic';

export default function PrivacyPolicy() {
  return (
    <main className="min-h-screen px-4 py-8 text-zinc-100 sm:px-6 lg:px-8">
      <section className="surface mx-auto max-w-3xl rounded-md p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-300">ZvZ Name</p>
        <h1 className="mt-3 text-2xl font-bold text-white">Politica de Privacidade</h1>
        <div className="mt-5 space-y-4 text-sm leading-6 text-zinc-300">
          <p>
            O ZvZ Name coleta apenas os dados necessarios para autenticar usuarios, organizar eventos e registrar
            check-ins.
          </p>
          <p>
            Os dados podem incluir identificador e nome do Discord, nick do Albion, builds liberadas, participacoes,
            montarias selecionadas e historico de check-ins.
          </p>
          <p>
            As informacoes sao usadas para controle interno da guilda, analise de participacao e validacao de acesso a
            eventos. Nao vendemos dados e nao compartilhamos informacoes com terceiros para publicidade.
          </p>
          <p>
            O login com Discord utiliza OAuth2. O aplicativo solicita permissoes somente para identificar o usuario e,
            quando habilitado, consultar informacoes basicas de guildas e membro para validacao.
          </p>
          <p>
            Usuarios podem solicitar remocao ou correcao de dados entrando em contato com a administracao da guilda.
          </p>
        </div>
      </section>
    </main>
  );
}
