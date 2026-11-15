# Ginástica em Dia 💜

Sistema web desenvolvido para facilitar a gestão de colaboradores e o acompanhamento da participação em aulas de ginástica laboral.

O projeto foi desenvolvido como parte do Projeto Integrador da Universidade Virtual do Estado de São Paulo (UNIVESP), com o objetivo de oferecer uma solução digital para organizar informações, registrar presenças e acompanhar indicadores relacionados às atividades de ginástica laboral nas empresas.

## Tecnologias utilizadas

- **Python:** desenvolvimento da lógica do sistema.
- **Flask:** framework utilizado para a aplicação web.
- **SQLite:** banco de dados para armazenamento das informações.
- **HTML e CSS:** estrutura e estilização das páginas.
- **JavaScript:** recursos de interação na interface.
- **Git e GitHub:** versionamento e armazenamento do código.

## Funcionalidades

O sistema possui dois perfis de acesso: responsável pela empresa e colaborador.

### Área da empresa

- Acesso ao painel administrativo.
- Cadastro e gerenciamento de colaboradores.
- Edição de informações, turnos, status e senhas dos colaboradores.
- Cadastro e gerenciamento dos turnos de ginástica laboral.
- Definição dos dias da semana e horários das aulas.
- Consulta de relatórios mensais de participação.
- Visualização da quantidade de presenças e colaboradores participantes.
- Acompanhamento das presenças por turno.
- Criação de pesquisas NPS com período de participação definido.
- Consulta da quantidade de respostas e do resultado NPS das pesquisas.

### Área do colaborador

- Cadastro utilizando o código fornecido pela empresa.
- Acesso individual por e-mail e senha.
- Visualização do turno e horário das aulas.
- Registro de presença nos dias programados.
- Limitação de um registro de presença por dia.
- Consulta de pesquisas NPS disponíveis.
- Envio de avaliações de 0 a 10, com comentário opcional.
- Encerramento da sessão por meio da opção de sair da conta.

## Banco de dados

O sistema utiliza SQLite e possui seis tabelas principais:

- `empresas`: informações das empresas cadastradas.
- `usuarios`: dados dos responsáveis e colaboradores.
- `turnos`: organização dos horários e dias das aulas.
- `presencas`: registros de participação dos colaboradores.
- `pesquisas_nps`: pesquisas criadas pelas empresas.
- `respostas_nps`: avaliações enviadas pelos colaboradores.

O arquivo `database/criar_banco.py` contém a estrutura necessária para criar as tabelas.

O banco de dados utilizado durante o desenvolvimento não está incluído no repositório.

## Como executar o projeto

**1. Clone o repositório:**

```bash
git clone https://github.com/juuhnicolette-a11y/sistema-ginastica-laboral.git
```

**2. Acesse a pasta do projeto:**

```bash
cd sistema-ginastica-laboral
```

**3. Crie e ative um ambiente virtual:**

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows, a ativação pode ser feita com:

```bash
.venv\Scripts\activate
```

**4. Instale o Flask:**

```bash
pip install Flask
```

**5. Crie o banco de dados:**

```bash
python database/criar_banco.py
```

**6. Inicie a aplicação:**

```bash
python app.py
```

Acesse o endereço indicado no terminal, normalmente `http://127.0.0.1:5000`.

**Observação:** a criação do banco gera as tabelas, mas não cadastra automaticamente uma empresa ou um usuário responsável. Para utilizar o painel administrativo em uma instalação nova, é necessário cadastrar esses dados inicialmente.

## Regras de funcionamento

- Cada colaborador pode estar vinculado a um turno.
- O check-in é permitido somente nos dias programados para as aulas.
- Cada colaborador pode registrar uma presença por dia.
- Apenas usuários ativos de empresas ativas podem acessar o sistema.
- Cada colaborador pode responder uma única vez a cada pesquisa NPS.
- As pesquisas ficam disponíveis somente durante o período definido pela empresa.
- As senhas são armazenadas utilizando hash.
- Os resultados NPS são apresentados de forma agregada, sem identificar individualmente os respondentes na interface da empresa.

## Objetivo do projeto

O Ginástica em Dia busca substituir controles manuais por uma ferramenta digital que facilite o registro de presenças, a organização dos turnos e o acompanhamento da participação dos colaboradores.

A proposta também contempla a coleta de avaliações por meio de pesquisas NPS, oferecendo informações que podem apoiar a melhoria contínua das atividades de ginástica laboral.

## Contexto acadêmico

**Instituição:** Universidade Virtual do Estado de São Paulo (UNIVESP)  
**Projeto:** Projeto Integrador em Computação  
**Ano:** 2026  
**Sistema:** Ginástica em Dia

Projeto desenvolvido para fins acadêmicos, com foco na aplicação prática de conhecimentos de desenvolvimento web, programação, banco de dados e experiência do usuário.