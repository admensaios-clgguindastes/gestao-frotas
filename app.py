from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Gestão de Frotas & Manutenção - Hits Acústico",
    page_icon="🚚",
    layout="wide",
)

# Arquivo JSON para persistência centralizada dos dados (multi-usuário)
DATA_FILE = "fleet_data.json"


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)

  initial_data = {
      "vehicles": [
          {
              "plate": "ABC-1234",
              "model": "Fiat Fiorino",
              "driver": "Equipe Som 1",
              "km": 45000,
              "preventive_km": 50000,
          },
          {
              "plate": "XYZ-9876",
              "model": "Renault Master",
              "driver": "Equipe Palco",
              "km": 78000,
              "preventive_km": 80000,
          },
          {
              "plate": "DEF-5678",
              "model": "Hyundai HR",
              "driver": "Logística Geral",
              "km": 31000,
              "preventive_km": 40000,
          },
      ],
      "workshop": [],
      "history": [],
  }
  save_data(initial_data)
  return initial_data


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


if "data" not in st.session_state:
  st.session_state.data = load_data()

data = st.session_state.data

# Cabeçalho Principal
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 20px; border-bottom: 1px solid #334155;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background-color: #4f46e5; padding: 10px; border-radius: 12px; color: white; font-size: 20px;">
                🚚
            </div>
            <div>
                <h1 style="margin: 0; font-size: 22px; font-weight: bold; color: #f8fafc;">Hits Acústico</h1>
                <p style="margin: 0; font-size: 13px; color: #94a3b8;">Gestão de Manutenção de Frotas (Multi-usuário)</p>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Abas de Navegação
tab_dash, tab_workshop, tab_vehicles, tab_history = st.tabs([
    "📊 Dashboard da Frota",
    f"🛠️ Veículos Parados ({len(data['workshop'])})",
    "🚐 Veículos & Quilometragem",
    "📋 Histórico de Serviços",
])

# ---------------------------------------------------------
# ABA 1: DASHBOARD
# ---------------------------------------------------------
with tab_dash:
  st.subheader("Visão Geral da Frota")

  total_v = len(data["vehicles"])
  workshop_v = len(data["workshop"])
  total_cost = sum([item.get("cost", 0) for item in data["history"]])

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total de Veículos", total_v)
  col2.metric("Na Oficina", workshop_v)
  col3.metric("Serviços Realizados", len(data["history"]))
  col4.metric(
      "Custo Total da Frota",
      f"R$ {total_cost:,.2f}".replace(",", "X")
      .replace(".", ",")
      .replace("X", "."),
  )

  st.markdown("### Status Atual dos Veículos")
  if total_v == 0:
    st.info("Nenhum veículo cadastrado.")
  else:
    cols = st.columns(3)
    for idx, v in enumerate(data["vehicles"]):
      with cols[idx % 3]:
        st.markdown(
            f"""
                <div style="background: #1e293b; padding: 18px; border-radius: 14px; border: 1px solid #334155; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                    <h4 style="margin:0 0 6px 0; color:#f8fafc; font-size: 16px;">{v['plate']} - {v['model']}</h4>
                    <p style="margin:0; font-size:13px; color:#94a3b8;">Responsável: <b style="color: #e2e8f0;">{v['driver']}</b></p>
                    <hr style="margin: 10px 0; border:0; border-top:1px solid #334155;">
                    <p style="margin:0; font-size:13px; color:#cbd5e1;">KM Atual: <b style="color: #38bdf8;">{v['km']:,} km</b></p>
                    <p style="margin:0; font-size:13px; color:#cbd5e1;">Revisão Preventiva: <b style="color: #facc15;">{v['preventive_km']:,} km</b></p>
                </div>
                """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# ABA 2: VEÍCULOS PARADOS (OFICINA)
# ---------------------------------------------------------
with tab_workshop:
  st.subheader("Gerenciamento de Oficina")

  with st.expander("➕ Registrar Nova Entrada de Veículo na Oficina"):
    with st.form("entry_form"):
      plates = [v["plate"] for v in data["vehicles"]]
      if not plates:
        st.warning("Cadastre um veículo primeiro.")
        selected_plate = None
      else:
        selected_plate = st.selectbox("Selecione a Placa", plates)

      entry_km = st.number_input("KM de Entrada", min_value=0, value=0)
      reason = st.text_area("Motivo / Problema Relatado")
      submit_entry = st.form_submit_button("Enviar para Oficina")

      if submit_entry and selected_plate:
        new_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "plate": selected_plate,
            "km": entry_km,
            "entry_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "reason": reason,
        }
        data["workshop"].append(new_entry)
        save_data(data)
        st.success("Veículo enviado para a oficina com sucesso!")
        st.rerun()

  st.markdown("---")
  if not data["workshop"]:
    st.info("Nenhum veículo parado na oficina no momento.")
  else:
    for item in data["workshop"]:
      with st.container():
        st.markdown(
            f"""
                <div style="background: #2a1b1b; border: 1px solid #7f1d1d; padding: 18px; border-radius: 14px; margin-bottom: 15px;">
                    <h4 style="margin:0; color: #f87171;">🚨 {item['plate']} (Em Manutenção)</h4>
                    <p style="margin: 6px 0; font-size: 13px; color: #cbd5e1;"><b>Entrada:</b> {item['entry_date']} | <b>KM:</b> {item['km']}</p>
                    <p style="margin: 6px 0; font-size: 13px; color: #cbd5e1;"><b>Problema:</b> {item['reason']}</p>
                </div>
                """,
            unsafe_allow_html=True,
        )

        with st.form(f"checkout_{item['id']}"):
          st.text("Dados para Finalização (Baixa)")
          exit_km = st.number_input(
              "KM de Saída", min_value=item["km"], value=item["km"]
          )
          cost = st.number_input("Custo Total (R$)", min_value=0.0, value=0.0)
          supplier = st.text_input("Fornecedor / Oficina")
          classification = st.text_input(
              "Classificação (ex: Troca de Óleo, Freios)"
          )
          desc = st.text_area("Descrição detalhada / Peças trocadas")

          if st.form_submit_button("Concluir e Dar Baixa"):
            history_item = {
                "plate": item["plate"],
                "type": "Corretiva",
                "entry_date": item["entry_date"],
                "exit_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "km": exit_km,
                "cost": cost,
                "supplier": supplier,
                "classification": classification,
                "description": desc,
            }
            data["history"].append(history_item)
            data["workshop"] = [
                w for w in data["workshop"] if w["id"] != item["id"]
            ]

            for v in data["vehicles"]:
              if v["plate"] == item["plate"]:
                v["km"] = exit_km

            save_data(data)
            st.success("Manutenção concluída e registrada no histórico!")
            st.rerun()

# ---------------------------------------------------------
# ABA 3: VEÍCULOS & QUILOMETRAGEM (COM EDIÇÃO E EXCLUSÃO)
# ---------------------------------------------------------
with tab_vehicles:
  st.subheader("Gerenciamento de Veículos & KM")

  with st.expander("➕ Adicionar Novo Veículo"):
    with st.form("new_vehicle_form"):
      new_plate = st.text_input("Placa do Veículo (ex: ABC-1234)")
      new_model = st.text_input("Modelo (ex: Fiat Fiorino)")
      new_driver = st.text_input("Responsável / Equipe")
      new_km = st.number_input("KM Atual", min_value=0, value=0)
      new_prev = st.number_input(
          "KM para Próxima Preventiva", min_value=0, value=10000
      )

      if st.form_submit_button("Salvar Veículo"):
        if new_plate:
          # Evita placa duplicada
          if any(v["plate"] == new_plate for v in data["vehicles"]):
            st.error("Já existe um veículo cadastrado com esta placa!")
          else:
            data["vehicles"].append({
                "plate": new_plate,
                "model": new_model,
                "driver": new_driver,
                "km": new_km,
                "preventive_km": new_prev,
            })
            save_data(data)
            st.success("Veículo cadastrado com sucesso!")
            st.rerun()
        else:
          st.error("A placa é obrigatória.")

  st.markdown("---")
  st.markdown("### Lista de Veículos Atuais")

  if not data["vehicles"]:
    st.info("Nenhum veículo cadastrado.")
  else:
    for idx, v in enumerate(data["vehicles"]):
      with st.container():
        col_info, col_btn1, col_btn2 = st.columns([4, 1, 1])

        with col_info:
          st.markdown(
              f"""
                    <div style="background: #1e293b; padding: 12px 16px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 8px;">
                        <b>{v['plate']}</b> — {v['model']} | <b>Responsável:</b> {v['driver']} | <b>KM Atual:</b> {v['km']:,} km (Preventiva: {v['preventive_km']:,} km)
                    </div>
                    """,
              unsafe_allow_html=True,
          )

        with col_btn1:
          if st.button("✏️ Editar", key=f"edit_{idx}"):
            st.session_state[f"editing_{v['plate']}"] = True

        with col_btn2:
          if st.button("🗑️ Excluir", key=f"del_{idx}"):
            data["vehicles"] = [
                item for item in data["vehicles"] if item["plate"] != v["plate"]
            ]
            save_data(data)
            st.success(f"Veículo {v['plate']} excluído com sucesso!")
            st.rerun()

        # Se clicou em editar, abre um formulário integrado para atualizar os dados
        if st.session_state.get(f"editing_{v['plate']}", False):
          with st.form(f"form_edit_{v['plate']}"):
            st.markdown(f"**Editando Veículo: {v['plate']}**")
            ed_model = st.text_input("Modelo", value=v["model"])
            ed_driver = st.text_input("Responsável", value=v["driver"])
            ed_km = st.number_input("KM Atual", min_value=0, value=v["km"])
            ed_prev = st.number_input(
                "KM Preventiva", min_value=0, value=v["preventive_km"]
            )

            col_s1, col_s2 = st.columns(2)
            with col_s1:
              if st.form_submit_button("Salvar Alterações"):
                v["model"] = ed_model
                v["driver"] = ed_driver
                v["km"] = ed_km
                v["preventive_km"] = ed_prev
                save_data(data)
                st.session_state[f"editing_{v['plate']}"] = False
                st.success("Alterações salvas com sucesso!")
                st.rerun()
            with col_s2:
              if st.form_submit_button("Cancelar"):
                st.session_state[f"editing_{v['plate']}"] = False
                st.rerun()

# ---------------------------------------------------------
# ABA 4: HISTÓRICO DE SERVIÇOS
# ---------------------------------------------------------
with tab_history:
  st.subheader("Histórico de Manutenções")

  if not data["history"]:
    st.info("Nenhum serviço registrado até o momento.")
  else:
    df_history = pd.DataFrame(data["history"])
    st.dataframe(df_history, use_container_width=True)

    csv = df_history.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Histórico em CSV (Excel)",
        data=csv,
        file_name="historico_manutencao_frotas.csv",
        mime="text/csv",
    )
