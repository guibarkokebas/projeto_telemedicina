# Plataforma de Telemedicina

Projeto final da disciplina **Implementação de Bancos de Dados NoSQL**. A aplicação simula um atendimento de telemedicina, da entrada na fila ao registro da consulta no prontuário, usando Python e Streamlit.

**Em desenvolvimento.** O repositório já inclui a tela inicial e uma base com 10 pacientes fictícios, incluindo dois idosos. As telas e os scripts de carga dos bancos fazem parte das próximas entregas.

## Arquitetura

| Banco | Papel na aplicação |
| --- | --- |
| MongoDB Atlas | Armazenar pacientes, profissionais, prontuários, receitas e laudos. |
| Redis Cloud | Ordenar a fila da recepção com Sorted Sets, controlar sessões e manter a agenda do dia em cache. |
| Neo4j AuraDB | Relacionar pacientes, médicos, diagnósticos e medicamentos. Consultas Cypher exibem diagnósticos correlacionados e alertas de incompatibilidade cadastrados para a simulação. |

## Executar no Windows

Na pasta do repositório, abra o PowerShell e rode os comandos abaixo com Python 3.12.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço indicado em **Local URL** no terminal. Para encerrar, pressione **Ctrl + C**.

### Configurar os bancos

Para desenvolver os módulos que acessam os bancos na nuvem, copie o modelo de configuração.

```powershell
Copy-Item .env.example .env
```

Preencha o arquivo local com as credenciais das suas instâncias.

| Variáveis | Serviço |
| --- | --- |
| `MONGODB_URI` | String de conexão do MongoDB Atlas |
| `REDIS_URL` | URL de conexão do Redis Cloud |
| `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` | URI e credenciais do Neo4j AuraDB |

Use somente dados fictícios e mantenha senhas e arquivos de credenciais fora dos commits.

## Contribuir

| Frente | Entrega |
| --- | --- |
| Recepção virtual | Fila de espera, agenda e início do atendimento com Redis. |
| Prontuário | Carga inicial, histórico, edição de diagnósticos e anexos com MongoDB. |
| Grafo clínico | Carga em Cypher, diagnósticos correlacionados e alertas simulados com Neo4j. |
| Finalização e integração | Registrar laudo ou receita, atualizar a fila e integrar as telas no Streamlit. |

Crie uma branch para sua tarefa e abra um pull request para `main`. Use `paciente_id` como referência entre os bancos. Os registros fictícios estão em [pacientes.json](pacientes.json).
