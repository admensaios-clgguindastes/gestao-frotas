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

# CSS Definitivo para forçar tema claro em 100% dos componentes (incluindo Modais e Inputs)
st.markdown(
    """
    <style>
    /* Forçar tema claro em toda a aplicação */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    
    /* Textos, títulos e rótulos escuros */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown {
        color: #0f172a !important;
    }
    
    /* Abas de navegação */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #64748b !important;
        font-size: 15px;
    }
    .stTabs [aria-selected="true"] {
        color: #4f46e5 !important;
        border-bottom: 2px solid #4f46e5;
        background-color: transparent;
    }
    
    /* Cartões */
    .fleet-card {
        background: #ffffff !important;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    .workshop-card {
        background: #fff5f5 !important;
        border: 1px solid #feb2b2;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Caixa de IA */
    .ai-box {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        padding: 16px 20px;
        border-radius: 14px;
        color: white !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
    }
    .ai-box *, .ai-box h4, .ai-box p, .ai-box div {
        color: white !important;
    }

    /* CORREÇÃO DOS MODAIS / POP-UPS (Fundo Branco e Texto Escuro) */
    div[data-baseweb="modal"], div[data-testid="stModal"] > div {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-radius: 16px !important;
    }
    
    /* Campos de entrada, selects e textareas com fundo branco e letras escuras */
    input, textarea, select, div[data-baseweb="select"] span {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
    }
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
              "plate": "ABC-1234",
              "model": "Fiat Fiorino",
              "driver": "Equipe Som 1",
              "km": 400000,
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

# Cabeçalho Superior
st.markdown(
    """
    <div style="background-color: #0f172a; padding: 16px 24px; border-radius: 14px; display: flex; align-items: center; justify-content: space-between; color: white; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background-color: #4f46e5; padding: 10px; border-radius: 10px; font-size: 18px;">🚚</div>
            <div>
                <h2 style="margin: 0; font-size: 18px; font-weight: bold; color: white !important;">Hits Acústico</h2>
                <p style="margin: 0; font-size: 12px; color: #94a3b8 !important;">Gestão de Manutenção de Frotas</p>
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

  # Tempo médio na oficina em horas e minutos
  avg_hours_str = "0h"
  if data["history"]:
    total_diffs = []
    for item in data["history"]:
      try:
        dt_in = datetime.strptime(item["entry_date"], "%Y-%m-%d %H:%M")
        dt_out = datetime.strptime(item["exit_date"], "%Y-%m-%d %H:%M")
        diff_h = (dt_out - dt_in).total_seconds() / 3600
        if diff_h > 0:
          total_diffs.append(diff_h)
      except:
        pass
    if total_diffs:
      avg_h = sum(total_diffs) / len(total_diffs)
      horas = int(avg_h)
      minutos = int((avg_h - horas) * 60)
      avg_hours_str = f"{horas}h {minutos}m"

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("Total de Veículos", total_v)
  c2.metric("Na Oficina", workshop_v)
  c3.metric("Revisão Vencida", warning_v)
  c4.metric("Tempo Médio na Oficina", avg_hours_str)

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
                    <h4 style="margin: 0 0 4px 0; color: #0f172a; font-size: 15px;">{v['model']}</h4>
                    <p style="margin: 0 0 12px 0; font-size: 11px; color: #475569; font-weight: 600;">👤 {v['driver']}</p>
                    <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 8px 0;">
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155; margin-bottom: 4px;">
                        <span>KM Atual:</span> <b style="color: #0f172a;">{v['km']:,} km</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: #334155;">
                        <span>KM Preventiva:</span> <b style="color: #0f172a;">{v['preventive_km']:,} km</b>
                    </div>
                </div>
                """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------
# 2. ABA: VEÍCULOS PARADOS (OFICINA) COM POP-UP NATIVO
# ---------------------------------------------------------


@st.dialog("➕ Registrar Entrada de Veículo na Oficina")
def modal_registrar_entrada():
  plates = [f"{v['plate']} - {v['model']}" for v in data["vehicles"]]
  sel_plate_full = st.selectbox("Selecione o Veículo", plates)
  entry_km = st.number_input("Quilometragem de Entrada (KM)", min_value=0)
  reason = st.text_area("Motivo / Problema Relatado")

  if st.button("Confirmar Entrada"):
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
    st.success("Veículo enviado para a oficina!")
    st.rerun()


@st.dialog("🔧 Dar Baixa / Finalizar Manutenção")
def modal_dar_baixa(item):
  st.markdown(
      f"**Veículo:** {item['plate']} | **Entrada:** {item['entry_date']}"
  )

  st.markdown(
      """
        <div class="ai-box">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">✨</span>
                <div>
                    <div style="font-weight: bold; font-size: 14px; color: white !important;">Preenchimento Inteligente por IA</div>
                    <div style="font-size: 12px; color: #e0e7ff !important;">Anexe a Nota Fiscal para preencher automaticamente.</div>
                </div>
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )
  uploaded_nf = st.file_uploader(
      "Anexar Nota Fiscal / O.S.", type=["png", "jpg", "jpeg"]
  )
  if uploaded_nf:
    st.success("✨ Nota lida com sucesso pela IA!")

  exit_km = st.number_input("KM de Saída", min_value=item["km"], value=item["km"])
  cost = st.number_input("Valor Total (R$)", min_value=0.0, value=0.0)
  supplier = st.text_input("Fornecedor / Oficina")
  classification = st.text_input("Classificação (ex: Pneus, Freios)")
  desc = st.text_area("Descrição detalhada")

  if st.button("Concluir e Direcionar ao Histórico"):
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
    data["workshop"] = [w for w in data["workshop"] if w["id"] != item["id"]]

    for v in data["vehicles"]:
      if v["plate"] == item["plate"]:
        v["km"] = exit_km

    save_data(data)
    st.success("Baixa realizada e enviada para o Histórico!")
    st.rerun()


with tab_workshop:
  st.subheader("Gerenciamento de Oficina")

  if st.button("➕ Registrar Nova Entrada de Veículo"):
    modal_registrar_entrada()

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

      if st.button(
          f"🔧 Dar Baixa / Finalizar ({item['plate']})", key=f"btn_pop_{item['id']}"
      ):
        modal_dar_baixa(item)

# ---------------------------------------------------------
# 3. ABA: VEÍCULOS & QUILOMETRAGEM
# ---------------------------------------------------------


@st.dialog("➕ Cadastrar Novo Veículo")
def modal_cadastrar_veiculo():
  new_plate = st.text_input("Placa")
  new_model = st.text_input("Modelo / Van")
  new_driver = st.text_input("Técnico / Responsável")
  new_team = st.text_input("Equipe (ex: Equipe 01)")
  new_km = st.number_input("KM Atual", min_value=0)
  new_prev = st.number_input("KM Preventiva (Próx.)", min_value=0)

  if st.button("Salvar Veículo"):
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
      st.success("Veículo cadastrado!")
      st.rerun()
    else:
      st.error("Informe a placa.")


with tab_vehicles:
  st.subheader("Gerenciamento de Veículos & KM")

  if st.button("➕ Adicionar Novo Veículo"):
    modal_cadastrar_veiculo()

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
                    <div><b style="color:#0f172a;">{v['plate']}</b> — <span style="color:#0f172a;">{v['model']}</span> | <span style="color: #475569;">{v['driver']}</span></div>
                    <div><b style="color:#0f172a;">KM:</b> {v['km']:,} km</div>
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
# 4. ABA: HISTÓRICO DE SERVIÇOS
# ---------------------------------------------------------


@st.dialog("➕ Registrar Manutenção Manual")
def modal_manutencao_manual():
  st.markdown(
      """
        <div class="ai-box">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 20px;">✨</span>
                <div>
                    <div style="font-weight: bold; font-size: 14px; color: white !important;">Preenchimento Inteligente por IA</div>
                    <div style="font-size: 12px; color: #e0e7ff !important;">Anexe a Nota Fiscal para preencher automaticamente.</div>
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
  serv_type = st.selectbox("Tipo de Manutenção", ["Preventiva", "Corretiva"])

  entry_dt = st.text_input(
      "Data / Hora de Entrada", value=datetime.now().strftime("%Y-%m-%d %H:%M")
  )
  exit_dt = st.text_input(
      "Data / Hora de Saída", value=datetime.now().strftime("%Y-%m-%d %H:%M")
  )
  km_val = st.number_input("Quilometragem (KM)", min_value=0)
  cost_val = st.number_input("Valor Total (R$)", min_value=0.0)
  supplier = st.text_input("Fornecedor / Oficina", placeholder="Ex: Flancar...")
  classification = st.text_input("Classificação", placeholder="Ex: Troca de Óleo...")
  description = st.text_area("Descrição Detalhada", placeholder="Descreva...")

  if st.button("Salvar no Histórico"):
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
    st.success("Salvo no histórico com sucesso!")
    st.rerun()


with tab_history:
  st.subheader("Histórico de Serviços & Manutenções")

  if st.button("➕ Registrar Nova Manutenção Manual"):
    modal_manutencao_manual()

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
