PROMPT COMPLETO — SISTEMA DE GERENCIAMENTO DE MEMBROS E CHECK-IN PARA ZVZ (ALBION ONLINE)

Você é um Arquiteto de Software Sênior e Desenvolvedor Full Stack. Sua tarefa é desenvolver uma aplicação web completa para gerenciamento de membros, participação em ZvZ e controle de builds de Albion Online.

O objetivo é criar um SaaS multi-guilda, porém com uma guilda principal (administradora) que terá acesso gratuito.

VISÃO GERAL

Desenvolver uma plataforma web onde:

Jogadores realizam cadastro único.
Jogadores informam suas armas principais.
Staff aprova ou reprova armas.
Antes de cada ZvZ o jogador realiza check-in.
O sistema contabiliza participações.
O sistema registra presença por arma.
O sistema gera estatísticas de presença.
O sistema gera rankings.
O sistema controla builds aprovadas.
Guildas pagantes podem utilizar o sistema isoladamente.
STACK TECNOLÓGICA
Frontend
Next.js 15
React
Typescript
TailwindCSS
Shadcn/UI
TanStack Query
Backend
FastAPI
SQLAlchemy
Alembic
Pydantic
Banco

Inicialmente:

Cloud SQL PostgreSQL (Google Cloud)

Caso o custo seja um problema:

Neon PostgreSQL

A aplicação deve funcionar em ambos.

Autenticação

Discord OAuth2

ESTRUTURA MULTI-TENANT

Criar suporte para múltiplas guildas.

Toda tabela deverá possuir:

guild_id

para isolamento dos dados.

TABELAS
guilds
id
name
discord_server_id
plan
active
created_at
users
id
guild_id

discord_id
discord_name

albion_nick

main_weapon_1
main_weapon_2

weapon_1_approved
weapon_2_approved

role

is_staff

rating

participations

created_at
updated_at
weapons
id

weapon_name
weapon_category

active
mounts
id

mount_name

active
zvz_events
id

guild_id

title

event_date

status

created_by

created_at
checkins
id

guild_id

event_id

user_id

weapon_selected

mount_selected

checkin_time

approved

notes
player_ratings
id

guild_id

player_id

staff_id

rating

comment

created_at
FLUXO DE CADASTRO
Primeiro acesso

Login via Discord.

Capturar:

{
  "discord_id": "",
  "discord_name": ""
}

Após login:

Solicitar:

Nick Albion
Arma principal 1
Arma principal 2

As armas devem vir de lista pré-definida.

APROVAÇÃO DE ARMAS

Somente Staff pode aprovar.

Exemplo:

Jogador:
Mello

Armas:
✓ Shadowcaller
✗ Realm Breaker

Se arma não estiver aprovada:

Não pode ser utilizada no check-in.

FLUXO DE CHECK-IN

Página pública:

/participar

Sem login.

Campos:

Nick Albion
Evento
Arma

Ao informar o nick:

Buscar jogador.

Validar:

Nick informado == Nick cadastrado

Se válido:

Exibir:

Armas aprovadas
Build da arma
Montarias permitidas
SELEÇÃO DE MONTARIA

Após escolher arma:

Mostrar apenas montarias permitidas para aquela build.

Exemplo:

Shadowcaller

Montarias:
- Frost Ram
- Direboar
- Spectral Bat
CONTADOR DE PARTICIPAÇÕES

Ao concluir check-in:

Incrementar:

participations + 1

na tabela users.

SISTEMA DE NOTAS

Todo jogador possui nota.

Padrão:

7

Staff pode alterar.

Exemplos:

Tank excelente = 9.5

DPS mediano = 6

Healer destaque = 10

Registrar histórico.

DASHBOARD STAFF

Criar dashboard com:

Presenças
Participações por jogador
Ranking
Top presentes
Ranking de notas
Top players
Uso de armas
Shadowcaller → 35%

Permafrost → 20%

Realm Breaker → 15%
Participações por período
7 dias
30 dias
90 dias
DASHBOARD DO JOGADOR

Exibir:

Minha Nota

Minhas Participações

Minhas Armas

Histórico de ZvZ
REGRAS DE NEGÓCIO
Nota inicial
rating = 7
Participações

Nunca decrementam.

Check-in duplicado

Bloquear.

Um jogador só pode realizar:

1 check-in por evento
Arma

Só pode selecionar:

Armas aprovadas
Montaria

Só pode selecionar:

Montarias compatíveis com a build
API
Auth
POST /auth/discord
GET /auth/me
Jogadores
POST /players

GET /players

GET /players/{id}

PUT /players/{id}
Eventos
POST /events

GET /events

PUT /events/{id}
Check-ins
POST /checkins

GET /checkins

GET /checkins/event/{id}
Dashboard
GET /dashboard/staff

GET /dashboard/player
DIFERENCIAL FUTURO

Preparar arquitetura para integração futura com:

Albion Online API

Buscar:

Kill Fame
PvP Fame
Guilda atual
Histórico de personagens
Discord Bot

Comandos:

/registrar

/checkin

/presenca

/ranking
QUALIDADE OBRIGATÓRIA

Antes de finalizar:

Criar migrations Alembic.
Criar Dockerfile.
Criar docker-compose.
Criar .env.example.
Criar documentação Swagger.
Criar seed inicial.
Criar testes unitários.
Criar testes de integração.
Implementar RBAC (Player / Staff / Admin).
Implementar auditoria de alterações.

O código deve seguir padrões de produção, arquitetura escalável, SOLID, Clean Architecture e estar preparado para milhares de jogadores e dezenas de guildas simultaneamente.