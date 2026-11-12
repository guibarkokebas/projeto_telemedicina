# Plataforma de Telemedicina

Projeto final da disciplina **Implementação de Bancos de Dados NoSQL**. A aplicação em Python e Streamlit simula a recepção virtual e a gestão de prontuários com dados fictícios.

## Funcionalidades

| Módulo | O que já funciona |
| --- | --- |
| Recepção virtual | Fila por ordem de chegada, com prioridade para os dois idosos da demonstração. O início do atendimento retira o primeiro paciente da fila e cria uma sessão de uma hora. |
| Agenda do dia | Um agendamento por paciente e um por horário na agenda compartilhada. Os horários aceitam intervalos de 30 minutos. |
| Prontuário | Consulta ao cadastro, registro e edição de diagnósticos e envio e download de laudos em PDF de até 5 MB. |

O grafo clínico e a finalização da consulta estão previstos para as próximas etapas.

## Arquitetura

| Banco | Papel na aplicação |
| --- | --- |
| MongoDB Atlas | Armazena pacientes, profissionais, especialidades, diagnósticos, laudos e agendamentos. |
| Redis Cloud | Ordena a fila com um Sorted Set, mantém tokens de sessão e guarda a agenda do dia em cache por cinco minutos. |
| Neo4j AuraDB | Previsto para relacionar pacientes, profissionais, diagnósticos e medicamentos e demonstrar alertas com consultas Cypher. |

## Executar no Windows

Clone o repositório e abra a pasta no PowerShell com Python 3.12 instalado.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha `MONGODB_URI` com a string de conexão do MongoDB Atlas e `REDIS_URL` com a URL do Redis Cloud. As variáveis `NEO4J_*` do modelo ficam reservadas para o módulo de grafo. Use dados fictícios e mantenha as credenciais no arquivo local `.env`.

```powershell
.\.venv\Scripts\python.exe carregar_mongodb.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

A carga cria o índice único de `paciente_id` e insere os cadastros que faltam a partir de [pacientes.json](pacientes.json), além de profissionais e especialidades fictícios. Abra a **Local URL** exibida no terminal. Para encerrar, pressione **Ctrl + C**.

## Demonstração

1. Em **Recepção Virtual**, adicione Rafael (`PAC004`) e depois Helena (`PAC001`). Confira a prioridade da Helena e tente adicioná-la novamente para ver o bloqueio de duplicatas.
2. Clique em **Iniciar próximo atendimento**. A primeira pessoa sai da fila, e a sessão ativa impede que ela volte à espera.
3. Na **Agenda do dia**, agende um horário livre como **14:30**. Tente repetir o horário com outro paciente e marcar um segundo horário para o primeiro. A tela deve bloquear as duas tentativas. Clique em **Atualizar fila** para ver a consulta da agenda pelo cache do Redis.
4. Em **Prontuário**, selecione Helena, registre e edite um diagnóstico fictício. Anexe um PDF de teste e baixe o arquivo para conferir.

## Contribuir

Crie uma branch para sua tarefa e abra um pull request para `main`. Use `paciente_id` como referência entre os bancos. As quatro frentes são recepção, prontuário, grafo clínico e finalização da consulta.
