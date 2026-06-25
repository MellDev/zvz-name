IMPLEMENTAÇÃO DE BUILDS E VALIDAÇÃO DE PARTICIPAÇÃO EM EVENTOS (ALBION ONLINE)

Analise todo o código existente antes de realizar qualquer alteração.

OBJETIVO

Implementar um sistema completo de Builds para eventos de Albion Online, permitindo que cada participante informe qual build utilizará durante o evento.

A implementação deve respeitar a arquitetura já existente do sistema, reaproveitando componentes, padrões, DAOs, Services, Controllers, Repositories e Models já utilizados.

ETAPA 1 — MODELAGEM DAS BUILDS

Criar uma entidade chamada:

Build

Campos:

id
nome
arma
offhand
capacete
peitoral
bota
capa
comida
pocao
montaria
nivel_requerido
criado_em
atualizado_em
ativo
ETAPA 2 — RELAÇÃO COM EVENTOS

Criar relacionamento:

Evento
    -> possui várias Builds

Build
    -> pertence a um Evento

Cada evento poderá possuir várias builds autorizadas.

Exemplo:

Evento ZvZ

Build:
- Tank Grovekeeper
- Tank Heavy Mace
- DPS Fire
- DPS Curse
- Healer Holy
ETAPA 3 — CHECK-IN COM BUILD

Após o jogador realizar o check-in do evento:

Ao invés de finalizar o processo imediatamente:

Abrir uma nova etapa:

Selecionar Build

O usuário deverá escolher uma build entre as builds liberadas para aquele evento.

Fluxo:

Entrar Evento
↓
Check-in
↓
Selecionar Build
↓
Confirmar Participação
ETAPA 4 — VALIDAÇÃO DE MONTARIA

Cada build deverá possuir:

montaria_recomendada

Exemplos:

Swiftclaw
Direwolf
Pest Lizard
Raven

Ao selecionar uma build:

Exibir ao usuário:

Build Selecionada

Arma: Grovekeeper
Montaria Recomendada: Swiftclaw
ETAPA 5 — TELA DE BUILDS

Criar menu:

Builds

Administradores poderão:

Criar Build

Campos:

Nome
Arma
Offhand
Capacete
Peitoral
Bota
Capa
Comida
Poção
Montaria
Editar Build
Excluir Build
Vincular Build ao Evento
ETAPA 6 — PARTICIPANTES

Na tela de participantes adicionar colunas:

Jogador
Build
Montaria
Horário Check-in
Status

Exemplo:

Anderson
Tank Grovekeeper
Swiftclaw
19:02
Confirmado
ETAPA 7 — DASHBOARD DO EVENTO

Adicionar métricas:

Total Participantes

Participantes por Build

Participantes por Função
(Tank, DPS, Healer, Support)

Montarias Utilizadas

Builds Mais Utilizadas
ETAPA 8 — DISTRIBUIÇÃO DE FUNÇÕES

Adicionar classificação automática das builds:

Tank
DPS
Healer
Support
Debuff
Bomb Squad

Cada build deverá possuir:

role

Exemplo:

Grovekeeper -> Tank
Blazing -> DPS
Holy Fallen -> Healer
ETAPA 9 — VALIDAÇÕES

Impedir:

Selecionar build inativa

Selecionar build não vinculada ao evento

Selecionar build excluída

Confirmar participação sem build
ETAPA 10 — EXPERIÊNCIA DO USUÁRIO

Após confirmar a build:

Exibir resumo:

Evento: ZvZ Fort Sterling

Build:
Tank Grovekeeper

Equipamentos:
- Grovekeeper
- Judicator Armor
- Guardian Helmet
- Hunter Shoes

Montaria:
Swiftclaw

Status:
Confirmado
REQUISITOS TÉCNICOS

Antes de implementar:

Mapear toda a estrutura atual do projeto.
Identificar Models existentes.
Identificar Services existentes.
Identificar Controllers existentes.
Identificar DAOs/Repositórios existentes.
Seguir exatamente o padrão arquitetural já utilizado.
Não criar código duplicado.
Reutilizar componentes visuais existentes.
Criar migrations necessárias.
Garantir compatibilidade com dados já existentes.

Ao final, gerar um relatório contendo:

Arquivos criados
Arquivos alterados
Tabelas criadas
Endpoints criados
Rotas criadas
Validações implementadas
Possíveis melhorias futuras