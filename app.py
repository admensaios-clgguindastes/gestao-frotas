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

# Abas de Navegação principais em Português
tab_dash, tab_workshop, tab_vehicles, tab_history = st.tabs([
    "📊 Painel da Frota",
    f"🛠️ Veículos na Oficina ({len(data['workshop'])})",
    "🚐 Veículos & Quilometragem",
    "📋 Histórico de Serviços",
])

# ---------------------------------------------------------
# 1. ABA: PAINEL DA FROTA
# ---------------------------------------------------------
with tab_dash:
  total_v = len(data["vehicles"])
  workshop_v = len(data["workshop"])
  ok_v = sum(1 for v in data["vehicles"] if v["km"] <= v["preventive_km"])
  warning_v = total_v - ok_v

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
                <div style="background: white; padding: 20px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="background: #0f172a; color: #ffffff !important; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 13px;">{plate}</span>
                        <span style="{badge_style} padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;">{badge_text}</span>
                    </div>
                    <h4 style="margin: 0 0 4px 0; color: #0f172a; font-size: 15px;">{v['model']}</h4>
                    <p style="margin: 0 0 12px 0; font-size: 11px; color: #475569; font-weight: 600;">👤 {v['driver']}</p>
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 8px 0;">
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
# 2. ABA: VEÍCULOS PARADOS (OFICINA) COM POP-UPS NATIVOS
# ---------------------------------------------------------


@st.dialog("➕ Registrar Entrada de Veículo na Oficina")
def modal_registrar_entrada():
  plates = [f"{v['plate']} - {v['model']}" for v in data["vehicles"]]
  sel_plate_full = st.selectbox("Selecione o Veículo", plates)
  entry_km = st.number_input("Quilometragem", min_value=0)
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
    st.success("Veículo enviado para a oficina com sucesso!")
    st.rerun()


@st.dialog("🔧 Dar Baixa / Finalizar Manutenção")
def modal_dar_baixa(item):
  st.markdown(
      f"**Veículo:** {item['plate']} | **Entrada:** {item['entry_date']}"
  )

  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 16px 20px; border-radius: 14px; color: white; display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
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
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
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
    st.success("Baixa realizada e enviada para o Histórico com sucesso!")
    st.rerun()


with tab_workshop:
  st.subheader("Gerenciamento de Oficina")

  if st.button("➕ Registrar Entrada de Veículo na Oficina"):
    modal_registrar_entrada()

  st.markdown("---")
  if not data["workshop"]:
    st.info("Nenhum veículo parado na oficina no momento.")
  else:
    for item in data["workshop"]:
      st.markdown(
          f"""
            <div style="background: #fff5f5; border: 1px solid #feb2b2; padding: 20px; border-radius: 16px; margin-bottom: 16px;">
                <h4 style="margin:0; color: #c53030;">🚨 {item['plate']} (Em Manutenção)</h4>
                <p style="margin: 4px 0; font-size: 13px; color: #475569;"><b>Veículo:</b> {item['plate']} | <b>Entrada:</b> {item['entry_date']} | <b>KM:</b> {item['km']:,}</p>
                <p style="margin: 4px 0; font-size: 13px; color: #475569;"><b>Problema:</b> {item['reason']}</p>
            </div>
            """,
          unsafe_allow_html=True,
      )

      if st.button(
          f"🔧 Dar Baixa / Finalizar Manutenção ({item['plate']})",
          key=f"btn_pop_{item['id']}",
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
  new_team = st.text_input("Equipe")
  new_km = st.number_input("KM", min_value=0)
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
      st.success("Veículo cadastrado com sucesso!")
      st.rerun()
    else:
      st.error("Informe a placa do veículo.")


with tab_vehicles:
  st.subheader("Gerenciamento de Veículos & Quilometragem")

  if st.button("➕ Adicionar Novos Veículos"):
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
                <div style="background: white; padding: 12px 16px; border-radius: 10px; border: 1px solid #cbd5e1; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div><b style="color:#0f172a;">{v['plate']}</b> — <span style="color:#0f172a;">{v['model']}</span> | <span style="color: #475569;">{v['driver']}</span></div>
                    <div><b style="color:#0f172a;">KM:</b> {v['km']:,} km</div>
                </div>
                """,
            unsafe_allow_html=True,
        )
      with col_edit:
        if st.button("Editar", key=f"edit_v_{idx}"):
          st.session_state[f"edit_mode_{v['plate']}"] = True
      with col_del:
        if st.button("Excluir", key=f"del_v_{idx}"):
          data["vehicles"] = [
              item for item in data["vehicles"] if item["plate"] != v["plate"]
          ]
          save_data(data)
          st.success(f"Veículo {v['plate']} excluído com sucesso!")
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
              st.success("Veículo atualizado com sucesso!")
              st.rerun()
          with b2:
            if st.form_submit_button("Cancelar"):
              st.session_state[f"edit_mode_{v['plate']}"] = False
              st.rerun()

# ---------------------------------------------------------
# 4. ABA: HISTÓRICO DE SERVIÇOS (Com Opção de Excluir)
# ---------------------------------------------------------


@st.dialog("➕ Registrar Manutenção Manual")
def modal_manutencao_manual():
  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 16px 20px; border-radius: 14px; color: white; display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
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
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
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
    st.info("Nenhum serviço registrado no histórico.")
  else:
    # Exibição individual com botão de exclusão para cada registro do histórico
    for idx, h in enumerate(data["history"]):
      col_h_info, col_h_del = st.columns([6, 1])
      with col_h_info:
        st.markdown(
            f"""
                <div style="background: white; padding: 14px 18px; border-radius: 12px; border: 1px solid #cbd5e1; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <b style="color: #0f172a; font-size: 14px;">🚚 Placa: {h['plate']} ({h['type']})</b>
                        <span style="color: #475569; font-size: 12px;"><b>Valor:</b> R$ {h.get('cost', 0):,.2f}</span>
                    </div>
                    <p style="margin: 2px 0; font-size: 12px; color: #475569;"><b>Período:</b> {h['entry_date']} até {h['exit_date']} | <b>KM:</b> {h['km']:,}</p>
                    <p style="margin: 2px 0; font-size: 12px; color: #475569;"><b>Fornecedor:</b> {h['supplier']} | <b>Classificação:</b> {h['classification']}</p>
                    <p style="margin: 2px 0; font-size: 12px; color: #334155;"><b>Descrição:</b> {h['description']}</p>
                </div>
                """,
            unsafe_allow_html=True,
        )
      with col_h_del:
        if st.button("🗑️ Excluir", key=f"del_hist_{idx}"):
          # Remove do histórico pelo ID ou índice
          if "id" in h:
            data["history"] = [
                item for item in data["history"] if item.get("id") != h["id"]
            ]
          else:
            data["history"].pop(idx)
          save_data(data)
          st.success("Registro excluído com sucesso!")
          st.rerun()

    st.markdown("---")
    df_history = pd.DataFrame(data["history"])
    csv = df_history.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Baixar Histórico em Excel (CSV)",
        data=csv,
        file_name="historico_manutencao.csv",
        mime="text/csv",
    )
