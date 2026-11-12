import json
import os
from datetime import date, timedelta
from secrets import token_urlsafe
from time import time

import streamlit as st
from pymongo.errors import DuplicateKeyError, PyMongoError
from redis import Redis
from redis.exceptions import RedisError, WatchError

CHAVE_FILA = "telemedicina:recepcao:fila"
PACIENTES_PRIORITARIOS = {"PAC001", "PAC002"}
# A faixa de pontuação prioritária vem antes da fila comum no Sorted Set.
DESCONTO_PRIORIDADE_MS = 10**13
DURACAO_SESSAO = 60 * 60


def chave_sessao(paciente_id):
    return f"telemedicina:recepcao:sessao:{paciente_id}"


def adicionar_paciente(redis, paciente_id, pontuacao):
    sessao = chave_sessao(paciente_id)
    with redis.pipeline() as operacao:
        operacao.watch(sessao)
        if operacao.exists(sessao):
            return "ativo"
        operacao.multi()
        operacao.zadd(CHAVE_FILA, {paciente_id: pontuacao}, nx=True)
        adicionado, = operacao.execute()
        return "adicionado" if adicionado else "na_fila"


def iniciar_proximo(redis):
    with redis.pipeline() as operacao:
        operacao.watch(CHAVE_FILA)
        proximo = operacao.zrange(CHAVE_FILA, 0, 0)
        if not proximo:
            return None
        paciente_id = proximo[0]
        sessao = chave_sessao(paciente_id)
        operacao.watch(sessao)
        if operacao.exists(sessao):
            return None

        operacao.multi()
        operacao.set(sessao, token_urlsafe(32), ex=DURACAO_SESSAO)
        operacao.zrem(CHAVE_FILA, paciente_id)
        operacao.execute()
        return paciente_id



@st.cache_resource
def conectar_redis(url):
    return Redis.from_url(
        url, decode_responses=True, socket_connect_timeout=5, socket_timeout=5
    )


def mostrar_recepcao(cadastros, agendamentos):
    url = os.getenv("REDIS_URL")
    if not url:
        st.info("Preencha REDIS_URL no arquivo .env do projeto.")
        return

    paciente_id = st.selectbox(
        "Paciente",
        options=list(cadastros),
        format_func=lambda codigo: f"{cadastros[codigo].get('nome', codigo)} · {codigo}",
        index=None,
        placeholder="Selecione um paciente",
    )
    entrada, atendimento, atualizar = st.columns(3)
    adicionar = entrada.button("Adicionar à fila", disabled=paciente_id is None)
    iniciar = atendimento.button("Iniciar próximo atendimento", type="primary")
    atualizar.button("Atualizar fila")

    try:
        redis = conectar_redis(url)
        if adicionar:
            pontuacao = int(time() * 1000)
            if paciente_id in PACIENTES_PRIORITARIOS:
                pontuacao -= DESCONTO_PRIORIDADE_MS
            estado = adicionar_paciente(redis, paciente_id, pontuacao)
            if estado == "adicionado":
                st.success("Paciente adicionado à fila.")
            elif estado == "ativo":
                st.info("Esse paciente já está em atendimento.")
            else:
                st.info("Esse paciente já está na fila.")

        if iniciar:
            atendido = iniciar_proximo(redis)
            if atendido:
                nome = cadastros.get(atendido, {}).get("nome", atendido)
                st.success(f"Atendimento iniciado para {nome}. Sessão válida por 1 hora.")
            else:
                st.info("Não há paciente disponível para iniciar.")

        fila = redis.zrange(CHAVE_FILA, 0, -1)
    except WatchError:
        st.warning("A fila mudou. Atualize a fila e tente novamente.")
        return
    except (RedisError, ValueError):
        st.error("Não foi possível acessar a fila. Confira a REDIS_URL e a conexão.")
        return

    fila_painel, agenda_painel = st.columns(2)
    with agenda_painel.container(border=True):
        mostrar_agenda(redis, agendamentos, cadastros, paciente_id)
    with fila_painel.container(border=True):
        mostrar_fila(fila, cadastros)


def mostrar_fila(fila, cadastros):

    st.subheader("Fila de espera")
    if not fila:
        st.info("A fila está vazia.")
        return

    st.table([
        {
            "Posição": posicao,
            "Paciente": cadastros.get(codigo, {}).get("nome", codigo),
            "Especialidade": cadastros.get(codigo, {}).get("especialidade_escolhida", "—"),
            "Prioridade": "Sim" if codigo in PACIENTES_PRIORITARIOS else "Comum",
        }
        for posicao, codigo in enumerate(fila, start=1)
    ])


def mostrar_agenda(redis, agendamentos, cadastros, paciente_id):
    st.subheader("Agenda do dia")
    hoje = date.today().isoformat()
    chave = f"telemedicina:recepcao:agenda:{hoje}"

    with st.form("agendar_consulta"):
        horario = st.time_input("Horário da consulta de hoje", value=None, step=timedelta(minutes=30))
        agendar = st.form_submit_button("Agendar paciente selecionado")

    if agendar and (paciente_id is None or horario is None):
        st.warning("Selecione um paciente e um horário para agendar.")
    elif agendar and (horario.minute not in (0, 30) or horario.second or horario.microsecond):
        st.warning("Escolha um horário terminado em :00 ou :30.")
    elif agendar:
        hora = horario.strftime("%H:%M")
        try:
            agendamentos.create_index(
                [("data", 1), ("hora", 1)],
                unique=True,
                partialFilterExpression={"horario_exclusivo": True},
                name="horario_exclusivo_por_dia",
            )
            filtro_paciente = {"data": hoje, "paciente_id": paciente_id}
            if agendamentos.find_one(filtro_paciente, {"_id": 1}):
                st.info("Esse paciente já tem um agendamento hoje.")
            elif agendamentos.find_one({"data": hoje, "hora": hora}, {"_id": 1}):
                st.warning("Esse horário já está ocupado. Escolha outro.")
            else:
                resultado = agendamentos.update_one(
                    filtro_paciente,
                    {"$setOnInsert": {
                        "_id": f"{hoje}:{paciente_id}",
                        "hora": hora,
                        "horario_exclusivo": True,
                    }},
                    upsert=True,
                )
                if resultado.upserted_id:
                    st.success("Consulta agendada.")
                    try:
                        redis.delete(chave)
                    except RedisError:
                        st.warning("O agendamento está no MongoDB. O cache será renovado quando expirar.")
                else:
                    st.info("Esse paciente já tem um agendamento hoje.")
        except DuplicateKeyError:
            st.warning("O horário ou o paciente acabou de ser agendado. Atualize a agenda.")
        except PyMongoError:
            st.error("Não foi possível gravar o agendamento no MongoDB.")

    try:
        cache = redis.get(chave)
    except RedisError:
        cache = None

    if cache is None:
        try:
            agenda = list(agendamentos.find(
                {"data": hoje}, {"_id": 0, "hora": 1, "paciente_id": 1}
            ).sort([("hora", 1), ("paciente_id", 1)]))
        except PyMongoError:
            st.error("Não foi possível consultar a agenda no MongoDB.")
            return
        try:
            redis.set(chave, json.dumps(agenda), ex=300, nx=True)
        except RedisError:
            st.caption("Agenda consultada no MongoDB. Cache indisponível.")
        else:
            st.caption("Agenda consultada no MongoDB.")
    else:
        agenda = json.loads(cache)
        st.caption("Agenda consultada no cache do Redis.")

    if not agenda:
        st.info("Nenhum agendamento para hoje.")
        return

    st.table([
        {
            "Horário": item["hora"],
            "Paciente": cadastros.get(item["paciente_id"], {}).get("nome", item["paciente_id"]),
        }
        for item in agenda
    ])
