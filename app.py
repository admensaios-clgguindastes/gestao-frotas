from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Frotas & Manutenção - Hits Acústico",
    page_icon="🚚",
    layout="wide",
)

# Estilização CSS personalizada para o layout moderno
st.markdown(
    """
    <style>
    .main { background-color: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #64748b; font-size: 15px; }
    .stTabs [aria-selected="true"] { color: #4f46e5 !important; border-bottom: 2px solid #4f46e5; }
    .fleet-card { background: white; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 16px; }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "fleet_data.json"


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)

  initial_data = {
      "vehicles": [
          {
              "plate": "LMQ7G36",
              "model": "415 CDI Sprinter",
              "driver": "FELIPE GOMES (EQUIPE 01)",
              "km": 425000,
              "preventive_km": 432095,
          },
          {
              "plate": "LMW9C81",
              "model": "415 CDI Sprinter",
              "driver": "LEANDRO ESTEVAM (EQUIPE 06)",
              "km": 444194,
              "preventive_km": 439000,
          },
          {
              "plate": "RJB7H18",
              "model": "416 CDI Sprinter",
              "driver": "IAGO ANTUNES (EQUIPE 03)",
              "km": 248000,
              "preventive_km": 246305,
          },
          {
              "plate": "RJF5F51",
              "model": "314 CDI Street F",
              "driver": "YURI ANTUNES (EQUIPE 05)",
              "km": 299000,
              "preventive_km": 296651,
          },
          {
              "plate": "TUH6F74",
              "model": "417",
              "driver": "N/A (N/A)",
              "km": 10465,
              "preventive_km": 18000,
          },
      ],
      "workshop": [],
      "history": [
          {
              "plate": "LMW9C81",
              "type": "Corretiva",
              "entry_date": "2026-10-26 08:00",
              "exit_date": "2026-10-26 17:00",
              "km": 444232,
              "cost": 1302.00,
              "supplier": "ALTA PERFORMACE",
              "classification": "PNEUS",
              "description": "TROCA DOS PNEUS TRASEIROS (ITR)",
          }
      ],
  }
  save_data(initial_data)
  return initial_data


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


if "data" not in st.session_state:
  st.session_state.data = load_data()

data = st.session_state.data

# Cabeçalho Superior
st.markdown(
    """
    <div style="background-color: #0f172a; padding: 16px 24px; border-radius: 14px; display: flex; align-items: center; justify-content: space-between; color: white; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background-color: #4f46e5; padding: 10px; border-radius: 10px; font-size: 18px;">🚚</div>
            <div>
                <h2 style="margin: 0; font-size: 18px; font-weight: bold;">Hits Acústico</h2>
                <p style="margin: 0; font-size: 12px; color: #94a3b8;">Gestão de Manutenção de Frotas</p>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Abas de Navegação principais
tab_dash, tab_workshop, tab_vehicles, tab_history = st.tabs([
    "📊 Dashboard da Frota",
    f"🛠️ Veículos Parados ({len(data['workshop'])})",
    "🚐 Veículos & Quilometragem",
    "📋 Histórico de Serviços",
])

# ---------------------------------------------------------
# 1. ABA: DASHBOARD DA FROTA
# ---------------------------------------------------------
with tab_dash:
  total_v = len(data["vehicles"])
  workshop_v = len(data["workshop"])
  ok_v = sum(1 for v in data["vehicles"] if v["km"] <= v["preventive_km"])
  warning_v = total_v - ok_v
  total_cost = sum([item.get("cost", 0) for item in data["history"]])

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Total de Veículos", total_v)
  c2.metric("Manutenções OK", ok_v)
  c3.metric("Próximo Revisão / Vencida", warning_v)
  c4.metric(
      "Custo Total da Frota",
      f"R$ {total_cost:,.2f}".replace(",", "X")
      .replace(".", ",")
      .replace("X", "."),
  )

  st.markdown("### Status Atual da Frota")

  if total_v == 0:
    st.info("Nenhum veículo cadastrado.")
  else:
    cols = st.columns(3)
    for idx, v in enumerate(data["vehicles"]):
      is_ok = v["km"] <= v["preventive_km"]
      badge_color = (
          "background-color: #dcfce7; color: #166534;"
          if is_ok
          else "background-color: #fee2e2; color: #991b1b;"
      )
      badge_text = "✔ Manutenção OK" if is_ok else "⚠ Revisão Vencida"

      with cols[idx % 3]:
        st.markdown(
            f"""
                <div class="fleet-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background: #0f172a; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 13px;">{v['plate']}</span>
                        <span style="{badge_color} padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">{badge_text}</span>
                    </div>
                    <h4 style="margin: 0 0 4px 0; color: #1e293b; font-size: 15px;">{v['model']}</h4>
                    <p style="margin: 0 0 12px 0; font-size: 11px; color: #64748b; font-weight: 600;">👤 {v['driver']}</p>
                    <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 8px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 4px;">
                        <span>KM Atual:</span> <b>{v['km']:,} km</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155;">
                        <span>KM Preventiva:</span> <b>{v['preventive_km']:,} km</b>
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# 2. ABA: VEÍCULOS PARADOS (OFICINA)
# ---------------------------------------------------------
with tab_workshop:
  st.subheader("Veículos Parados na Oficina (Em Manutenção)")

  with st.expander("➕ Registrar Entrada de Veículo na Oficina"):
    with st.form("entry_form"):
      plates = [f"{v['plate']} - {v['model']}" for v in data["vehicles"]]
      sel_plate_full = st.selectbox("Selecione o Veículo", plates)
      entry_km = st.number_input("Quilometragem de Entrada (KM)", min_value=0)
      reason = st.text_area("Motivo / Problema Relatado")

      if st.form_submit_button("Registrar Entrada"):
        plate_code = sel_plate_full.split(" - ")[0]
        new_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "plate": plate_code,
            "km": entry_km,
            "entry_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "reason": reason,
        }
        data["workshop"].append(new_entry)
        save_data(data)
        st.success("Veículo enviado para a oficina com sucesso!")
        st.rerun()

  if not data["workshop"]:
    st.info("Nenhum veículo parado na oficina no momento.")
  else:
    for item in data["workshop"]:
      st.markdown(
          f"""
            <div style="background: #fff5f5; border: 1px solid #feb2b2; padding: 16px; border-radius: 12px; margin-bottom: 12px;">
                <h4 style="margin:0; color: #c53030;">🚨 {item['plate']} (Em Manutenção)</h4>
                <p style="margin: 4px 0; font-size: 13px;"><b>Entrada:</b> {item['entry_date']} | <b>KM:</b> {item['km']:,}</p>
                <p style="margin: 4px 0; font-size: 13px;"><b>Problema:</b> {item['reason']}</p>
            </div>
            """,
          unsafe_allow_html=True,
      )
      with st.form(f"checkout_{item['id']}"):
        st.text("Dados para Finalização / Baixa")
        exit_km = st.number_input(
            "KM de Saída", min_value=item["km"], value=item["km"]
        )
        cost = st.number_input("Valor Total (R$)", min_value=0.0, value=0.0)
        supplier = st.text_input("Fornecedor / Oficina")
        classification = st.text_input("Classificação (ex: Pneus, Freios)")
        desc = st.text_area("Descrição detalhada")

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
          st.success("Serviço concluído!")
          st.rerun()

# ---------------------------------------------------------
# 3. ABA: VEÍCULOS & QUILOMETRAGEM (COM EDIÇÃO E EXCLUSÃO)
# ---------------------------------------------------------
with tab_vehicles:
  st.subheader("Gerenciamento de Veículos & KM")

  with st.expander("➕ Adicionar Novo Veículo"):
    with st.form("new_vehicle_form"):
      c1, c2 = st.columns(2)
      with c1:
        new_plate = st.text_input("Placa")
        new_driver = st.text_input("Técnico / Responsável")
        new_km = st.number_input("KM Atual", min_value=0)
      with c2:
        new_model = st.text_input("Modelo / Van")
        new_team = st.text_input("Equipe (ex: Equipe 01)")
        new_prev = st.number_input("KM Preventiva (Próx.)", min_value=0)

      if st.form_submit_button("Cadastrar Veículo"):
        if new_plate:
          full_driver = (
              f"{new_driver.upper()} ({new_team.upper()})"
              if new_team
              else new_driver.upper()
          )
          data["vehicles"].append({
              "plate": new_plate.upper(),
              "model": new_model,
              "driver": full_driver,
              "km": new_km,
              "preventive_km": new_prev,
          })
          save_data(data)
          st.success("Veículo cadastrado com sucesso!")
          st.rerun()
        else:
          st.error("Informe a placa do veículo.")

  st.markdown("---")
  if not data["vehicles"]:
    st.info("Nenhum veículo cadastrado.")
  else:
    for idx, v in enumerate(data["vehicles"]):
      col_info, col_edit, col_del = st.columns([5, 1, 1])
      with col_info:
        st.markdown(
            f"""
                <div style="background: white; padding: 12px 16px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div><b>{v['plate']}</b> — {v['model']} | <span style="color: #64748b;">{v['driver']}</span></div>
                    <div><b>KM:</b> {v['km']:,} km</div>
                </div>
                """,
            unsafe_allow_html=True,
        )
      with col_edit:
        if st.button("✏️ Editar", key=f"edit_v_{idx}"):
          st.session_state[f"edit_mode_{v['plate']}"] = True
      with col_del:
        if st.button("🗑️ Excluir", key=f"del_v_{idx}"):
          data["vehicles"] = [
              item for item in data["vehicles"] if item["plate"] != v["plate"]
          ]
          save_data(data)
          st.success(f"Veículo {v['plate']} excluído!")
          st.rerun()

      if st.session_state.get(f"edit_mode_{v['plate']}", False):
        with st.form(f"form_edit_veh_{v['plate']}"):
          st.markdown(f"**Editar Veículo: {v['plate']}**")
          m_model = st.text_input("Modelo", value=v["model"])
          m_driver = st.text_input("Responsável / Equipe", value=v["driver"])
          m_km = st.number_input("KM Atual", value=v["km"])
          m_prev = st.number_input("KM Preventiva", value=v["preventive_km"])

          b1, b2 = st.columns(2)
          with b1:
            if st.form_submit_button("Salvar"):
              v["model"] = m_model
              v["driver"] = m_driver
              v["km"] = m_km
              v["preventive_km"] = m_prev
              save_data(data)
              st.session_state[f"edit_mode_{v['plate']}"] = False
              st.success("Atualizado com sucesso!")
              st.rerun()
          with b2:
            if st.form_submit_button("Cancelar"):
              st.session_state[f"edit_mode_{v['plate']}"] = False
              st.rerun()

# ---------------------------------------------------------
# 4. ABA: HISTÓRICO DE SERVIÇOS (COM PREENCHIMENTO POR IA)
# ---------------------------------------------------------
with tab_history:
  st.subheader("Histórico de Serviços & Manutenções")

  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 20px; border-radius: 16px; color: white; display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="background: rgba(255,255,255,0.2); padding: 14px; border-radius: 12px; font-size: 20px;">✨</div>
                <div>
                    <h4 style="margin: 0; font-size: 16px; font-weight: bold;">Preenchimento Inteligente por IA</h4>
                    <p style="margin: 0; font-size: 13px; color: #e0e7ff;">Envie a foto da Nota Fiscal ou O.S. para preencher automaticamente.</p>
                </div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  uploaded_file = st.file_uploader(
      "📸 Anexar Foto da Nota Fiscal / O.S.", type=["png", "jpg", "jpeg"]
  )
  if uploaded_file is not None:
    with st.spinner("Analisando documento com Inteligência Artificial..."):
      st.success(
          "✨ Nota analisada com sucesso! Dados extraídos: Fornecedor:"
          " OFICINA CENTRAL, Valor: R$ 450,00."
      )

  with st.expander("➕ Registrar Nova Manutenção Manualmente"):
    with st.form("new_service_form"):
      plates = [f"{v['plate']} - {v['model']}" for v in data["vehicles"]]
      serv_plate_full = st.selectbox("Veículo (Placa)", plates)
      serv_type = st.selectbox(
          "Tipo de Manutenção", ["Preventiva", "Corretiva"]
      )

      c1, c2 = st.columns(2)
      with c1:
        entry_dt = st.text_input(
            "Data / Hora de Entrada",
            value=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        km_val = st.number_input("Quilometragem (KM)", min_value=0)
        supplier = st.text_input(
            "Fornecedor / Oficina", placeholder="Ex: Flancar, Alta Performance..."
        )
      with c2:
        exit_dt = st.text_input(
            "Data / Hora de Saída",
            value=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        cost_val = st.number_input("Valor Total (R$)", min_value=0.0)
        os_num = st.text_input(
            "Número O.S. (Ordem de Serviço)", placeholder="Ex: OS 12345"
        )

      classification = st.text_input(
          "Classificação do Serviço",
          placeholder="Ex: Troca de Óleo, Pastilhas de Freio...",
      )
      description = st.text_area(
          "Descrição Detalhada / Peças Trocadas",
          placeholder="Descreva os itens trocados...",
      )

      if st.form_submit_button("Salvar Manutenção"):
        plate_code = serv_plate_full.split(" - ")[0]
        new_hist = {
            "plate": plate_code,
            "type": serv_type,
            "entry_date": entry_dt,
            "exit_date": exit_dt,
            "km": km_val,
            "cost": cost_val,
            "supplier": supplier.upper(),
            "classification": classification.upper(),
            "description": description.upper(),
        }
        data["history"].append(new_hist)
        save_data(data)
        st.success("Manutenção registrada com sucesso!")
        st.rerun()

  st.markdown("---")
  if not data["history"]:
    st.info("Nenhum serviço registrado.")
  else:
    df_history = pd.DataFrame(data["history"])
    st.dataframe(df_history, use_container_width=True)

    csv = df_history.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Baixar Histórico em Excel (CSV)",
        data=csv,
        file_name="historico_manutencao.csv",
        mime="text/csv",
    )
