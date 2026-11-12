from html import escape

import streamlit as st


def mostrar_cabecalho(titulo, descricao):
    st.markdown(
        """
        <style>
        .telemedicina-cabecalho {
            position: relative;
            overflow: hidden;
            isolation: isolate;
            margin-bottom: 0.8rem;
            padding: clamp(1.35rem, 4vw, 2.75rem);
            border: 1px solid #519c924d;
            border-radius: 1.35rem;
            background: linear-gradient(115deg, #519c9210, #519c9233 70%, #347c8d30);
        }
        .telemedicina-cabecalho::after {
            content: "";
            position: absolute;
            z-index: -1;
            right: -4rem;
            top: -8rem;
            width: 23rem;
            aspect-ratio: 1;
            border-radius: 50%;
            background: repeating-radial-gradient(
                circle, transparent 0 22px, #519c9247 23px 24px
            );
            pointer-events: none;
            mask-image: linear-gradient(to left, black, transparent);
        }
        .telemedicina-cabecalho h1 {
            color: inherit;
            font-size: clamp(1.9rem, 4vw, 2.8rem);
            letter-spacing: -0.035em;
            padding: 0;
            margin: 0 0 0.4rem;
        }
        .telemedicina-cabecalho p {
            color: inherit;
            margin: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="telemedicina-cabecalho"><h1>{escape(titulo)}</h1>'
        f'<p>{escape(descricao)}</p></div>',
        unsafe_allow_html=True,
    )
