def load_data_from_github():
  # Para forçar a importação do Excel se o JSON antigo estiver vazio ou obsoleto,
  # vamos tentar ler o Excel primeiro se ele existir localmente/no repo.
  initial_history = []
  vehicles_dict = {}

  if os.path.exists(EXCEL_PATH):
    try:
      df_excel = pd.read_excel(EXCEL_PATH, skiprows=1)
      # Normaliza os nomes das colunas para maiúsculas e sem espaços extras
      df_excel.columns = [str(c).strip().upper() for c in df_excel.columns]

      for idx, row in df_excel.iterrows():
        plate = str(row.get("PLACA VEÍCULO", "")).strip().upper()
        if not plate or plate == "NAN" or plate == "NONE":
          continue

        km_val = row.get("KM", 0)
        km = float(km_val) if pd.notnull(km_val) else 0

        date_raw = row.get("DATA", datetime.now())
        date_str = (
            str(date_raw)[:10] + " 00:00"
            if pd.notnull(date_raw)
            else datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        supplier = str(row.get("FORNECEDOR", "N/A") or "N/A").strip()
        val_raw = row.get("VALOR R$", 0)
        cost = float(val_raw) if pd.notnull(val_raw) else 0.0

        t_man = str(row.get("TIPO MAN.", "Corretiva") or "Corretiva").strip()
        t_man = "Preventiva" if "PREV" in t_man.upper() else "Corretiva"

        classif = str(
            row.get("CLASSIFICAÇÃO DE MANUTENÇÃO", "MANUTENÇÃO")
            or "MANUTENÇÃO"
        ).strip()
        desc = str(row.get("SERVIO DETALHADO", "") or "").strip()

        initial_history.append({
            "id": f"excel_{idx}",
            "plate": plate,
            "type": t_man,
            "entry_date": date_str,
            "exit_date": date_str,
            "km": int(km),
            "cost": cost,
            "supplier": supplier.upper(),
            "classification": classif.upper(),
            "description": desc.upper(),
        })

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
      print(f"Erro ao ler Excel: {e}")

  # Se conseguiu ler do Excel, monta os dados e grava no GitHub/JSON
  if initial_history:
    initial_data = {
        "vehicles": list(vehicles_dict.values()),
        "workshop": [],
        "history": initial_history,
    }
    save_data_to_github(initial_data)
    return initial_data, None

  # Fallback caso não ache o Excel: tenta ler do GitHub JSON
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

  # Estrutura padrão vazia final
  default_data = {
      "vehicles": [{
          "plate": "ABC-1234",
          "model": "Fiat Fiorino",
          "driver": "Equipe Som 1",
          "km": 40000,
          "preventive_interval": 10000,
          "preventive_km": 50000,
      }],
      "workshop": [],
      "history": [],
  }
  save_data_to_github(default_data)
  return default_data, None
