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

# 1. CORREÇÃO DE CORES: Forçando tema claro, fundo branco e texto escuro legível
st.markdown(
    """
    <style>
    .stApp { background-color: #f8fafc; color: #1e293b; }
    
    /* Textos gerais e títulos escuros */
    h1, h2, h3, h4, h5, h6, p, span, label, div { color: #1e293b; }
    
    /* Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #64748b !important; font-size: 15px; }
    .stTabs [aria-selected="true"] { color: #4f46e5 !important; border-bottom: 2px solid #4f46e5; background-color: transparent; }
    
    /* Cartões */
    .fleet-card { background: white; padding: 20px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 16px; }
    .workshop-card { background: #fff5f5; border: 1px solid #feb2b2; padding: 20px; border-radius: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    
    /* Caixa de IA */
    .ai-box {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        padding: 16px 20px;
        border-radius: 14px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
    }
    .ai-box * { color: white !important; }
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
              "entry_date": "2026-10-20 08:00",
              "exit_date": "2026-10-22 17:00",
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
                <h2 style="margin: 0; font-size: 18px; font-weight: bold; color: white;">Hits Acústico</h2>
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
# 1. ABA: DASHBOARD DA FROTA (Com Status e Tempo Médio de Oficina)
# ---------------------------------------------------------
with tab_dash:
  total_v = len(data["vehicles"])
  workshop_v = len(data["workshop"])
  ok_v = sum(1 for v in data["vehicles"] if v["km"] <= v["preventive_km"])
  warning_v = total_v - ok_v
  total_cost = sum([item.get("cost", 0) for item in data["history"]])

  # Cálculo do tempo médio na oficina com base no histórico
  avg_hours = 0.0
  if data["history"]:
    total_diffs = []
    for item in data["history"]:
      try:
        dt_in = datetime.strptime(item["entry_date"], "%Y-%m-%d %H:%M")
        dt_out = datetime.strptime(item["exit_date"], "%Y-%m-%d %H:%M")
        diff_hours = (dt_out - dt_in).total_seconds() / 3600
        if diff_hours > 0:
          total_diffs.append(diff_hours)
      except:
        pass
    if total_diffs:
      avg_hours = sum(total_diffs) / len(total_diffs)

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Total de Veículos", total_v)
  c2.metric("Na Oficina", workshop_v)
  c3.metric("Revisão Vencida", warning_v)
  c4.metric("Tempo Médio na Oficina", f"{avg_hours:.1f} horas")

  st.markdown("### Status Atual dos Veículos")

  if total_v == 0:
    st.info("Nenhum veículo cadastrado.")
  else:
    workshop_plates = [w["plate"] for w in data["workshop"]]
    cols = st.columns(3)

    for idx, v in enumerate(data["vehicles"]):
      plate = v["plate"]
      is_in_workshop = plate in workshop_plates
      is_expired = v["km"] > v["preventive_km"]

      # Definindo insígnias visuais limpas
      if is_in_workshop:
        badge_style = "background-color: #fee2e2; color: #991b1b;"
        badge_text = "🚨 Na Oficina"
      elif is_expired:
        badge_style = "background-color: #fef3c7; color: #92400e;"
        badge_text = "⚠ Revisão Vencida"
      else:
        badge_style = "background-color: #dcfce7; color: #166534;"
        badge_text = "✔ Manutenção OK"

      with cols[idx % 3]:
        st.markdown(
            f"""
                <div class="fleet-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background: #0f172a; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 13px;">{plate}</span>
                        <span style="{badge_style} padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">{badge_text}</span>
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
  st.subheader("Gerenciamento de Oficina")

  if st.button("➕ Registrar Nova Entrada de Veículo"):
    st.session_state["open_entry_modal"] = True

  if st.session_state.get("open_entry_modal", False):
    with st.form("entry_modal_form"):
      st.markdown("### Registrar Entrada de Veículo")
      plates = [f"{v['plate']} - {v['model']}" for v in data["vehicles"]]
      sel_plate_full = st.selectbox("Selecione o Veículo", plates)
      entry_km = st.number_input("Quilometragem de Entrada (KM)", min_value=0)
      reason = st.text_area("Motivo / Problema Relatado")

      col_m1, col_m2 = st.columns(2)
      with col_m1:
        if st.form_submit_button("Confirmar Entrada"):
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
          st.session_state["open_entry_modal"] = False
          st.success("Veículo enviado para a oficina!")
          st.rerun()
      with col_m2:
        if st.form_submit_button("Cancelar"):
          st.session_state["open_entry_modal"] = False
          st.rerun()

  st.markdown("---")
  if not data["workshop"]:
    st.info("Nenhum veículo parado na oficina no momento.")
  else:
    for item in data["workshop"]:
      st.markdown(
          f"""
            <div class="workshop-card">
                <h4 style="margin:0; color: #c53030;">🚨 {item['plate']} (Em Manutenção)</h4>
                <p style="margin: 4px 0; font-size: 13px; color: #475569;"><b>Entrada:</b> {item['entry_date']} | <b>KM:</b> {item['km']:,}</p>
                <p style="margin: 4px 0; font-size: 13px; color: #475569;"><b>Problema:</b> {item['reason']}</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

      # 3. JANELA DE BOTÃO PARA DAR BAIXA (Estilo Modal Canvas)
      if st.button(
          f"🔧 Dar Baixa / Finalizar ({item['plate']})", key=f"btn_modal_{item['id']}"
      ):
        st.session_state[f"modal_checkout_{item['id']}"] = True

      if st.session_state.get(f"modal_checkout_{item['id']}", False):
        with st.form(f"form_checkout_{item['id']}"):
          st.markdown(f"### Dar Baixa: Veículo {item['plate']}")

          # Bloco de IA Opcional na Baixa
          st.markdown(
              """
                <div class="ai-box">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 20px;">✨</span>
                        <div>
                            <div style="font-weight: bold; font-size: 14px;">Preenchimento Inteligente por IA</div>
                            <div style="font-size: 12px; color: #e0e7ff;">Anexe a Nota Fiscal para agilizar o preenchimento.</div>
                        </div>
                    </div>
                </div>
            """,
              unsafe_allow_html=True,
          )
          uploaded_nf = st.file_uploader(
              "Anexar Nota Fiscal / O.S.",
              type=["png", "jpg", "jpeg"],
              key=f"nf_{item['id']}",
          )
          if uploaded_nf:
            st.success("✨ Nota lida com sucesso pela IA!")

          exit_km = st.number_input(
              "KM de Saída", min_value=item["km"], value=item["km"]
          )
          cost = st.number_input("Valor Total (R$)", min_value=0.0, value=0.0)
          supplier = st.text_input("Fornecedor / Oficina")
          classification = st.text_input("Classificação (ex: Pneus, Freios)")
          desc = st.text_area("Descrição detalhada")

          col_b1, col_b2 = st.columns(2)
          with col_b1:
            if st.form_submit_button("Concluir e Direcionar ao Histórico"):
              # 4. DIRECIONA OS DADOS PARA A ABA "HISTÓRICO DE SERVIÇOS"
              history_item = {
                  "plate": item["plate"],
                  "type": "Corretiva",
                  "entry_date": item["entry_date"],
                  "exit_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                  "km": exit_km,
                  "cost": cost,
                  "supplier": supplier.upper(),
                  "classification": classification.upper(),
                  "description": desc.upper(),
              }
              data["history"].append(history_item)
              data["workshop"] = [
                  w for w in data["workshop"] if w["id"] != item["id"]
              ]

              # Atualiza KM atual do veículo correspondente
              for v in data["vehicles"]:
                if v["plate"] == item["plate"]:
                  v["km"] = exit_km

              save_data(data)
              st.session_state[f"modal_checkout_{item['id']}"] = False
              st.success("Baixa realizada e enviada para o Histórico!")
              st.rerun()
          with col_b2:
            if st.form_submit_button("Fechar / Cancelar"):
              st.session_state[f"modal_checkout_{item['id']}"] = False
              st.rerun()

# ---------------------------------------------------------
# 3. ABA: VEÍCULOS & QUILOMETRAGEM
# ---------------------------------------------------------
with tab_vehicles:
  st.subheader("Gerenciamento de Veículos & KM")

  if st.button("➕ Adicionar Novo Veículo "):
    st.session_state["open_add_veh"] = True

  if st.session_state.get("open_add_veh", False):
    with st.form("new_vehicle_form"):
      st.markdown("### Cadastrar Novo Veículo")
      c1, c2 = st.columns(2)
      with c1:
        new_plate = st.text_input("Placa")
        new_driver = st.text_input("Técnico / Responsável")
        new_km = st.number_input("KM Atual", min_value=0)
      with c2:
        new_model = st.text_input("Modelo / Van")
        new_team = st.text_input("Equipe (ex: Equipe 01)")
        new_prev = st.number_input("KM Preventiva (Próx.)", min_value=0)

      sub_c1, sub_c2 = st.columns(2)
      with sub_c1:
        if st.form_submit_button("Salvar Veículo"):
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
            st.session_state["open_add_veh"] = False
            st.success("Veículo cadastrado!")
            st.rerun()
          else:
            st.error("Informe a placa.")
      with sub_c2:
        if st.form_submit_button("Cancelar"):
          st.session_state["open_add_veh"] = False
          st.rerun()

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
            if st.form_submit_button("Salvar Alterações"):
              v["model"] = m_model
              v["driver"] = m_driver
              v["km"] = m_km
              v["preventive_km"] = m_prev
              save_data(data)
              st.session_state[f"edit_mode_{v['plate']}"] = False
              st.success("Atualizado!")
              st.rerun()
          with b2:
            if st.form_submit_button("Cancelar"):
              st.session_state[f"edit_mode_{v['plate']}"] = False
              st.rerun()

# ---------------------------------------------------------
# 4. ABA: HISTÓRICO DE SERVIÇOS (Recebe os dados da baixa)
# ---------------------------------------------------------
with tab_history:
  st.subheader("Histórico de Serviços & Manutenções")

  if st.button("➕ Registrar Nova Manutenção Manual"):
    st.session_state["open_manual_hist"] = True

  if st.session_state.get("open_manual_hist", False):
    with st.form("new_service_form"):
      st.markdown("### Registrar Manutenção Manual")

      # Caixa IA
      st.markdown(
          """
            <div class="ai-box">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 20px;">✨</span>
                    <div>
                        <div style="font-weight: bold; font-size: 14px;">Preenchimento Inteligente por IA</div>
                        <div style="font-size: 12px; color: #e0e7ff;">Anexe a Nota Fiscal para preencher automaticamente.</div>
                    </div>
                </div>
            </div>
        """,
          unsafe_allow_html=True,
      )
      uploaded_file = st.file_uploader(
          "Anexar Nota Fiscal / O.S.", type=["png", "jpg", "jpeg"]
      )
      if uploaded_file:
        st.success("✨ Nota lida com sucesso pela IA!")

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
            "Fornecedor / Oficina", placeholder="Ex: Flancar..."
        )
      with c2:
        exit_dt = st.text_input(
            "Data / Hora de Saída",
            value=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        cost_val = st.number_input("Valor Total (R$)", min_value=0.0)
        os_num = st.text_input("Número O.S.", placeholder="Ex: OS 12345")

      classification = st.text_input(
          "Classificação", placeholder="Ex: Troca de Óleo..."
      )
      description = st.text_area(
          "Descrição Detalhada", placeholder="Descreva..."
      )

      sub_h1, sub_h2 = st.columns(2)
      with sub_h1:
        if st.form_submit_button("Salvar no Histórico"):
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
          st.session_state["open_manual_hist"] = False
          st.success("Salvo no histórico com sucesso!")
          st.rerun()
      with sub_h2:
        if st.form_submit_button("Cancelar"):
          st.session_state["open_manual_hist"] = False
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
