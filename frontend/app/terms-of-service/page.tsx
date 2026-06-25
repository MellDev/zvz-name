export const dynamic = 'force-dynamic';

export default function TermsOfService() {
  return (
    <main className="min-h-screen px-4 py-8 text-zinc-100 sm:px-6 lg:px-8">
      <section className="surface mx-auto max-w-3xl rounded-md p-6">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-300">ZvZ Name</p>
        <h1 className="mt-3 text-2xl font-bold text-white">Termos de Servico</h1>
        <div className="mt-5 space-y-4 text-sm leading-6 text-zinc-300">
          <p>
            O ZvZ Name e uma ferramenta para organizacao de eventos, builds, vagas e check-ins de guildas no Albion
            Online.
          </p>
          <p>
            Ao usar o aplicativo, o usuario concorda em fornecer dados corretos para cadastro, autenticacao via Discord
            e participacao nos eventos organizados pela guilda.
          </p>
          <p>
            A equipe responsavel pode remover cadastros, bloquear builds, alterar eventos ou cancelar check-ins quando
            necessario para manter a organizacao da guilda.
          </p>
          <p>
            O aplicativo e fornecido sem garantia de disponibilidade continua. Manutencoes, falhas externas ou mudancas
            nas APIs do Discord, Albion Online ou Google Cloud podem afetar temporariamente o funcionamento.
          </p>
          <p>
            Estes termos podem ser atualizados conforme novas funcionalidades forem adicionadas ao sistema.
          </p>
        </div>
      </section>
    </main>
  );
}
