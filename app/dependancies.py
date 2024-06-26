import json
from datetime import datetime
import os
import sys
import psycopg2
import streamlit as st

# Adicionando o caminho para importação dos módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.connection import connect_to_postgresql
from utils.validations import *
from repo.users import get_user_emails, get_usernames, insert_user, verify_user
from repo.documents import update_user_cnh, update_user_rg, insert_user_cnh, insert_user_rg

# SQL queries:


# Functions app:
def sign_up():
    with st.form(key="signup", clear_on_submit=True):
        st.subheader(":green[Cadastrar]")
        email = st.text_input(":green[Email]", placeholder="Digite seu Email")
        username = st.text_input(
            ":green[Usuário]", placeholder="Digite seu Nome de Usuário"
        )
        password1 = st.text_input(
            ":green[Senha]", placeholder="Digite sua Senha", type="password"
        )
        password2 = st.text_input(
            ":green[Confirmar Senha]", placeholder="Confirme sua Senha", type="password"
        )

        if st.form_submit_button("Cadastrar"):

            if email:
                if validate_email(email):
                    if email not in get_user_emails():
                        if validate_username(username):
                            if username not in get_usernames():
                                if len(username) >= 2:
                                    if len(password1) >= 6:
                                        if password1 == password2:
                                            insert_user(email, username, password1)
                                        else:
                                            st.warning("As senhas não correspondem")
                                    else:
                                        st.warning("A senha é muito curta")
                                else:
                                    st.warning("Nome de usuário muito curto")
                            else:
                                st.warning("Nome de usuário já existe")
                        else:
                            st.warning("Nome de usuário inválido")
                    else:
                        st.warning("Email já cadastrado")
                else:
                    st.warning("Email inválido")


def input_user_cnh(
    nome=None,
    rg=None,
    emissor=None,
    uf=None,
    cpf=None,
    data_nascimento=None,
    registro=None,
    verificador=None,
):

    with st.form(key="dados", clear_on_submit=True):
        st.subheader(":green_car[Dados CNH]")  # Correção do emoji
        nome = st.text_input(
            ":green_car[Nome]", value=nome, placeholder="Digite seu Nome Completo"
        )
        cpf = st.text_input(
            ":green_car[CPF]",
            value=cpf,
            placeholder="Digite seu CPF",
            help="Exemplo: 123.456.789-10",
        )
        rg = st.text_input(
            ":green_car[RG]",
            value=rg,
            placeholder="Digite seu RG",
            help="Exemplo: 1234567",
        )
        numero_validador = st.text_input(
            ":green_car[Número validador da CNH]",
            value=verificador,
            placeholder="Digite o número validador da CNH",
            help="Números na posição vertical",
        )
        numero_registro = st.text_input(
            ":green_car[Número de Registro da CNH]",
            value=registro,
            placeholder="Digite o número de Registro da CNH",
            help="Número de Registro",
        )
        org_emissor = st.text_input(
            ":green_car[Órgão Emissor]",
            value=emissor,
            placeholder="Digite o órgão emissor",
            help="Exemplo: SSP",
        )
        uf = st.text_input(
            ":green_car[UF]",
            value=uf,
            placeholder="Digite a UF",
            help="Siglas do estado em que a CNH foi emitida.",
        )
        # Alternativa para exibir o calendário
        if data_nascimento != None:
            data_nascimento = st.text_input(
                ":green_car[Data de nascimento]",
                value=data_nascimento,
                placeholder="DD/MM/YYYY",
            )

        else:
            data_nascimento = st.text_input(
                ":green_car[Data De nascimento]",
                value=data_nascimento,
                placeholder="DD/MM/YYYY",
                help="Sua data de nascimento.",
            )

        enviar_dados = st.form_submit_button("Enviar")
        if enviar_dados:
            if nome and validate_name(nome):
                if numero_validador:
                    if org_emissor:
                        if uf and len(uf) == 2:
                            if cpf and validate_cpf(cpf):
                                if data_nascimento:
                                    data_nascimento_obj = datetime.strptime(
                                        data_nascimento, "%d/%m/%Y"
                                    )
                                    postgres_date = data_nascimento_obj.strftime(
                                        "%Y-%m-%d"
                                    )
                                    dados = {
                                        "name": nome,
                                        "cpf_number": cpf,
                                        "validator_number": numero_validador,
                                        "registration_number": numero_registro,
                                        "issuing_body": org_emissor,
                                        "uf": uf,
                                        "birthdate": postgres_date,
                                        "rg_number": rg,
                                    }
                                    dados_json = json.dumps(dados)
                                    insert_user_cnh(dados_json)
                                else:
                                    st.warning("Insira a data de nascimento.")
                            else:
                                st.warning("Insira o CPF")
                        else:
                            st.warning("A UF deve ter dois dígitos.")
                    else:
                        st.warning("Insira o Órgão emissor.")
                else:
                    st.warning("Número inválido.")
            else:
                st.warning("Insira um nome válido.")


def input_user_rg(
    nome=None,
    rg=None,
    cpf=None,
    data_nascimento=None,
):

    with st.form(key="dados", clear_on_submit=True):
        st.subheader(":green_car[Dados RG]")
        nome = st.text_input(
            ":green_car[Nome]", value=nome, placeholder="Digite seu Nome Completo"
        )
        rg = st.text_input(
            ":green_car[RG]",
            value=rg,
            placeholder="Digite seu RG",
            help="Exemplo: 1234567",
        )

        cpf = st.text_input(
            ":green_car[CPF]",
            value=cpf,
            placeholder="Digite seu CPF",
            help="Exemplo: 123.456.789-10",
        )

        # Alternativa para exibir o calendário
        if data_nascimento != None:
            data_nascimento = st.text_input(
                ":green_car[Data de nascimento]",
                value=data_nascimento,
                placeholder="DD/MM/YYYY",
            )

        else:
            data_nascimento = st.text_input(
                ":green_car[Data De nascimento]",
                value=data_nascimento,
                placeholder="DD/MM/YYYY",
                help="Sua data de nascimento.",
            )

        enviar_dados = st.form_submit_button("Enviar")
        if enviar_dados:
            if nome and validate_name(nome):
                if cpf and validate_cpf(cpf):
                    if rg:
                        if data_nascimento:
                            data_nascimento_obj = datetime.strptime(
                                data_nascimento, "%d/%m/%Y"
                            )
                            postgres_date = data_nascimento_obj.strftime("%Y-%m-%d")
                            dados = {
                                "name": nome,
                                "cpf_number": cpf,
                                "rg_number": rg,
                                "birthdate": postgres_date,
                            }
                            dados_json = json.dumps(dados)
                            insert_user_rg(dados_json)
                        else:
                            st.warning("Insira a data de nascimento.")
                    else:
                        st.warning("Insira um RG válido.")
                else:
                    st.warning("Insira um CPF válido.")
            else:
                st.warning("Insira um nome válido.")


def input_update_user_cnh(
    name=None,
    rg_number=None,
    issuing_body=None,
    uf=None,
    cpf_number=None,
    birthdate=None,
    registration_number=None,
    validator_number=None,
):

    with st.form(key="dados", clear_on_submit=True):
        st.subheader(":green_car[Dados CNH]")  # Correção do emoji
        name = st.text_input(
            ":green_car[Nome]", value=name, placeholder="Digite seu Nome Completo"
        )
        cpf_number = st.text_input(
            ":green_car[CPF]",
            value=cpf_number,
            placeholder="Digite seu CPF",
            help="Exemplo: 123.456.789-10",
        )
        rg_number = st.text_input(
            ":green_car[RG]",
            value=rg_number,
            placeholder="Digite seu RG",
            help="Exemplo: 1234567",
        )
        validator_number = st.text_input(
            ":green_car[Número validador da CNH]",
            value=validator_number,
            placeholder="Digite o número validador da CNH",
            help="Números na posição vertical",
        )
        registration_number = st.text_input(
            ":green_car[Número de Registro da CNH]",
            value=registration_number,
            placeholder="Digite o número de Registro da CNH",
            help="Número de Registro",
        )
        issuing_body = st.text_input(
            ":green_car[Órgão Emissor]",
            value=issuing_body,
            placeholder="Digite o órgão emissor",
            help="Exemplo: SSP",
        )
        uf = st.text_input(
            ":green_car[UF]",
            value=uf,
            placeholder="Digite a UF",
            help="Siglas do estado em que a CNH foi emitida.",
        )
        # Alternativa para exibir o calendário
        if birthdate != None:
            birthdate = st.text_input(
                ":green_car[Data de nascimento]",
                value=birthdate,
                placeholder="DD/MM/YYYY",
            )

        else:
            birthdate = st.date_input(
                ":green_car[Data de nascimento]", value=None, format="DD/MM/YYYY"
            )

        enviar_dados = st.form_submit_button("Atualizar")
        if enviar_dados:
            if name and validate_name(name):
                if validator_number:
                    if issuing_body:
                        if uf and len(uf) == 2:
                            if cpf_number and validate_cpf(cpf_number):
                                if birthdate:
                                    dados = {
                                        "name": name,
                                        "cpf_number": cpf_number,
                                        "validator_number": validator_number,
                                        "registration_number": registration_number,
                                        "issuing_body": issuing_body,
                                        "uf": uf,
                                        "birthdate": birthdate,
                                        "rg_number": rg_number,
                                    }
                                    dados_json = json.dumps(dados)
                                    update_user_cnh(dados_json)
                                else:
                                    st.warning("Insira a data de nascimento.")
                            else:
                                st.warning("Insira o CPF")
                        else:
                            st.warning("A UF deve ter dois dígitos.")
                    else:
                        st.warning("Insira o Órgão emissor.")
                else:
                    st.warning("Número inválido.")
            else:
                st.warning("Insira um nome válido.")


def input_update_user_rg(
    name=None,
    rg_number=None,
    cpf_number=None,
    birthdate=None,
):
    with st.form(key="dados", clear_on_submit=True):
        st.subheader(":green_car[Dados RG]")
        name = st.text_input(
            ":green_car[Nome]", value=name, placeholder="Digite seu Nome Completo"
        )
        rg_number = st.text_input(
            ":green_car[RG]",
            value=rg_number,
            placeholder="Digite seu RG",
            help="Exemplo: 1234567",
        )

        cpf_number = st.text_input(
            ":green_car[CPF]",
            value=cpf_number,
            placeholder="Digite seu CPF",
            help="Exemplo: 123.456.789-10",
        )

        # Alternativa para exibir o calendário
        if birthdate != None:
            birthdate = st.text_input(
                ":green_car[Data de nascimento]",
                value=birthdate,
                placeholder="DD/MM/YYYY",
            )

        else:
            birthdate = st.date_input(
                ":green_car[Data de nascimento]", value=None, format="DD/MM/YYYY"
            )

        enviar_dados = st.form_submit_button("Atualizar")
        if enviar_dados:
            if name and validate_name(name):
                if cpf_number and validate_cpf(cpf_number):
                    if rg_number:
                        if birthdate:
                            dados = {
                                "name": name,
                                "cpf_number": cpf_number,
                                "rg_number": rg_number,
                                "birthdate": birthdate,
                            }
                            dados_json = json.dumps(dados)
                            update_user_rg(dados_json)
                        else:
                            st.warning("Insira a data de nascimento.")
                    else:
                        st.warning("Insira um RG válido.")
                else:
                    st.warning("Insira um CPF válido.")
            else:
                st.warning("Insira um nome válido.")
