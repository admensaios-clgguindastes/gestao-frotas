from datetime import datetime
import json
import os
import pandas as pd
import requests
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Frotas & Manutenção - Hits Acústico",
    page_icon="🚚",
    layout="wide",
)

# Configurações do GitHub para persistência permanente dos dados
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "seu-usuario/seu-repositorio")
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "seu_token_aqui")
FILE_PATH = "fleet_data.json"
EXCEL_PATH = "MANUTENÇÕES CLG.xlsx"


def load_data_from_github():
  # Tenta carregar do GitHub primeiro
  if GITHUB_TOKEN and GITHUB_REPO:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "vnd.github.v3+json",
    }
    try:
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
        file_content = response.json()
        import base64

        decoded_content = base64.b64decode(
            file_content["content"]
        ).decode("utf-8")
        return json.loads(decoded_content), file_content.get("sha")
    except Exception as e:
      print(f"Erro ao ler do GitHub: {e}")

  if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r", encoding="utf-8") as f:
      return json.load(f), None

  # Se não existir dados salvos, tenta importar do Excel enviado (MANUTENÇÕES CLG.xlsx)
  initial_history = []
  vehicles_dict = {}

  if os.path.exists(EXCEL_PATH):
    try:
      df_excel = pd.read_excel(EXCEL_PATH, skiprows=1)
      for idx, row in df_excel.iterrows():
        plate = str(row.get("PLACA VEÍCULO", "")).strip().upper()
        if not plate or plate == "NAN":
          continue

        km = float(row.get("KM", 0) or 0)
        date_raw = row.get("DATA", datetime.now())
        date_str = (
            str(date_raw)[:16]
            if pd.notnull(date_raw)
            else datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        supplier = str(row.get("FORNECEDOR", "N/A") or "N/A").strip()
        cost = float(row.get("VALOR R$", 0) or 0)
        t_man = str(row.get("TIPO MAN.", "Corretiva") or "Corretiva").strip()
        t_man = "Preventiva" if "PREV" in t_man.upper() else "Corretiva"
        desc = str(row.get("SERVIO DETALHADO", "") or "").strip()

        # Adiciona ao histórico
        initial_history.append({
            "id": f"excel_{idx}",
            "plate": plate,
            "type": t_man,
            "entry_date": date_str,
            "exit_date": date_str,
            "km": int(km),
            "cost": cost,
            "supplier": supplier.upper(),
            "classification": str(
                row.get("CLASSIFICAÇÃO DE MANUTENÇÃO", "MANUTENÇÃO")
            ).upper(),
            "description": desc.upper(),
        })

        # Mapeia veículos únicos encontrados no Excel
        if plate not in vehicles_dict or km > vehicles_dict[plate]["km"]:
          vehicles_dict[plate] = {
              "plate": plate,
              "model": "Veículo Frota CLG",
              "driver": "Equipe Técnica",
              "km": int(km),
              "preventive_interval": 10000,
              "preventive_km": int(km + 10000),
          }
    except Exception as e:
      print(f"Erro ao importar Excel: {e}")

  vehicles_list = (
      list(vehicles_dict.values())
      if vehicles_dict
      else [
          {
              "plate": "ABC-1234",
              "model": "Fiat Fiorino",
              "driver": "Equipe Som 1",
              "km": 40000,
              "preventive_interval": 10000,
              "preventive_km": 50000,
          }
      ]
  )

  initial_data = {
      "vehicles": vehicles_list,
      "workshop": [],
      "history": initial_history,
  }
  save_data_to_github(initial_data)
  return initial_data, None


def save_data_to_github(data_dict):
  with open(FILE_PATH, "w", encoding="utf-8") as f:
    json.dump(data_dict, f, ensure_ascii=False, indent=4)

  if GITHUB_TOKEN and GITHUB_REPO:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "vnd.github.v3+json",
    }

    sha = None
    try:
      resp = requests.get(url, headers=headers)
      if resp.status_code == 200:
        sha = resp.json().get("sha")
    except:
      pass

    import base64

    content_str = json.dumps(data_dict, ensure_ascii=False, indent=4)
    content_encoded = base64.b64encode(content_str.encode("utf-8")).decode(
        "utf-8"
    )

    payload = {
        "message": (
            "Atualização automática de dados da frota via Streamlit App"
        ),
        "content": content_encoded,
    }
    if sha:
      payload["sha"] = sha

    try:
      requests.put(url, headers=headers, json=payload)
    except Exception as e:
      print(f"Erro ao salvar no GitHub: {e}")


if "data" not in st.session_state:
  loaded, sha_val = load_data_from_github()
  st.session_state.data = loaded

data = st.session_state.data

# Cabeçalho Superior
st.markdown(
    """
    <div style="background-color: #0f172a; padding: 16px 24px; border-radius: 14px; display: flex; align-items: center; justify-content: space-between; color: white; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background-color: #4f46e5; padding: 10px; border-radius: 10px; font-size: 18px;">🚚</div>
            <div>
                <h2 style="margin: 0; font-size: 18px; font-weight: bold; color: white !important;">Hits Acústico & CLG Guindastes</h2>
                <p style="margin: 0; font-size: 12px; color: #94a3b8 !important;">Gestão de Manutenção de Frotas</p>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Abas de Navegação principais
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
  ok_v = sum(
      1
      for v in data["vehicles"]
      if v["km"] <= v.get("preventive_km", 0) - 1000
  )
  warning_v = total_v - ok_v

  avg_hours_str = "0h"
  if data["history"]:
    total_diffs = []
    for item in data["history"]:
      try:
        dt_in = datetime.strptime(item["entry_date"][:10], "%Y-%m-%d")
        dt_out = datetime.strptime(item["exit_date"][:10], "%Y-%m-%d")
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
  c3.metric("Revisão Próxima / Vencida", warning_v)
  c4.metric("Tempo Médio na Oficina", avg_hours_str)

  st.markdown("### Atualização Rápida de KM & Status dos Veículos")

  with st.expander("⚡ Atualizar Quilometragem Rápida de um Veículo"):
    with st.form("quick_km_form"):
      q_plates = [f"{v['plate']} - {v['model']}" for v in data["vehicles"]]
      sel_q_plate = st.selectbox("Selecione o Veículo", q_plates)
      new_q_km = st.number_input("Novo KM Atual", min_value=0, value=0)
      if st.form_submit_button("Atualizar KM"):
        plate_to_up = sel_q_plate.split(" - ")[0]
        for v in data["vehicles"]:
          if v["plate"] == plate_to_up:
            v["km"] = new_q_km
        save_data_to_github(data)
        st.success(f"Quilometragem do veículo {plate_to_up} atualizada!")
        st.rerun()

  st.markdown("---")

  if total_v == 0:
    st.info("Nenhum veículo cadastrado.")
  else:
    workshop_plates = [w["plate"] for w in data["workshop"]]
    cols = st.columns(3)

    for idx, v in enumerate(data["vehicles"]):
      plate = v["plate"]
      is_in_workshop = plate in workshop_plates
      prev_target = v.get("preventive_km", v["km"] + 10000)
      km_diff = prev_target - v["km"]

      if is_in_workshop:
        badge_style = "background-color: #fee2e2; color: #991b1b;"
        badge_text = "🚨 Na Oficina"
      elif km_diff <= 0:
        badge_style = "background-color: #fef3c7; color: #92400e;"
        badge_text = "⚠ Revisão Vencida!"
      elif km_diff <= 1500:
        badge_style = "background-color: #ffedd5; color: #c2410c;"
        badge_text = (
            f"⚠️ Revisão Próxima ({km_diff:,} km restantes)".replace(",", ".")
        )
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
                        <span>Próx. Revisão:</span> <b style="color: #0f172a;">{prev_target:,} km</b>
                    </div>
                </div>
                """.replace(
                ",", "."
            ),
            unsafe_allow_html=True,
        )

  # Relatórios & Custos no Painel da Frota
  st.markdown("---")
  st.subheader("📈 Relatórios Estatísticos & Custos de Manutenção")

  if not data["history"]:
    st.info(
        "Ainda não há registros no histórico para gerar relatórios e gráficos."
    )
  else:
    df_rep = pd.DataFrame(data["history"])
    df_rep["cost"] = pd.to_numeric(df_rep["cost"], errors="coerce").fillna(0)

    total_gasto = df_rep["cost"].sum()
    total_servicos = len(df_rep)
    custo_medio = total_gasto / total_servicos if total_servicos > 0 else 0

    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Custo Total da Frota", f"R$ {total_gasto:,.2f}".replace(",", "."))
    rc2.metric("Total de Intervenções", total_servicos)
    rc3.metric(
        "Custo Médio por Serviço", f"R$ {custo_medio:,.2f}".replace(",", ".")
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📊 Custo Total de Manutenção por Veículo (R$)")
    df_cost_plate = df_rep.groupby("plate")["cost"].sum().reset_index()
    df_cost_plate.columns = ["Placa", "Custo Total (R$)"]
    st.bar_chart
