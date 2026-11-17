from datetime import date, datetime, timedelta, timezone
import urllib.parse
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Social Media Planner & Scheduler (PAS & PTD)",
    page_icon="📱",
    layout="wide",
)

# Konfigurasi Akses Google Sheets via st.secrets
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_gspread_client():
  creds_dict = dict(st.secrets["gcp_service_account"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
  client = gspread.authorize(creds)
  return client


# Fungsi untuk memuat data utama (Jadwal Konten) dari Google Sheets
def load_database():
  try:
    client = get_gspread_client()
    sheet = client.open("Content Database Sosmed").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
      df = pd.DataFrame(
          columns=[
              "ID",
              "Kategori",
              "Judul Konten",
              "Platform",
              "Tipe Konten",
              "Jadwal Upload",
              "Link Google Drive",
              "Status",
              "Approval",
              "Approved By",
              "Catatan",
          ]
      )
    else:
      if "Kategori" not in df.columns:
        df.insert(1, "Kategori", "PAS")
      if "Approved By" not in df.columns:
        df["Approved By"] = "-"

      if "Tipe Konten" in df.columns:
        df["Tipe Konten"] = df["Tipe Konten"].apply(
            lambda x: x.split(", ") if isinstance(x, str) and x else []
        )
    return df
  except Exception as e:
    return pd.DataFrame(
        columns=[
            "ID",
            "Kategori",
            "Judul Konten",
            "Platform",
            "Tipe Konten",
            "Jadwal Upload",
            "Link Google Drive",
            "Status",
            "Approval",
            "Approved By",
            "Catatan",
        ]
    )


# Fungsi untuk menyimpan seluruh DataFrame utama ke Google Sheets
def save_database(df):
  try:
    client = get_gspread_client()
    sheet = client.open("Content Database Sosmed").sheet1

    df_to_save = df.copy()
    df_to_save["Tipe Konten"] = df_to_save["Tipe Konten"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    )

    sheet.clear()
    header = list(df_to_save.columns)
    rows = df_to_save.values.tolist()
    sheet.update([header] + rows)
  except Exception as e:
    st.error(f"Gagal menyimpan ke Google Sheets: {e}")


# ==========================================
# FUNGSI UNTUK REKAPAN REQUEST KONTEN
# ==========================================
def load_request_database():
  try:
    client = get_gspread_client()
    try:
      sheet = client.open("Content Database Sosmed").worksheet("Request Konten")
    except:
      spreadsheet = client.open("Content Database Sosmed")
      sheet = spreadsheet.add_worksheet(title="Request Konten", rows=100, cols=10)
      sheet.append_row([
          "ID", "Kategori", "Judul Request", "Platform", "Tipe Konten", 
          "Pengaju", "Link Referensi", "Status Request", "Catatan"
      ])
    
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
      df = pd.DataFrame(
          columns=[
              "ID",
              "Kategori",
              "Judul Request",
              "Platform",
              "Tipe Konten",
              "Pengaju",
              "Link Referensi",
              "Status Request",
              "Catatan",
          ]
      )
    else:
      if "Tipe Konten" in df.columns:
        df["Tipe Konten"] = df["Tipe Konten"].apply(
            lambda x: x.split(", ") if isinstance(x, str) and x else []
        )
    return df
  except Exception as e:
    return pd.DataFrame(
        columns=[
            "ID",
            "Kategori",
            "Judul Request",
            "Platform",
            "Tipe Konten",
            "Pengaju",
            "Link Referensi",
            "Status Request",
            "Catatan",
        ]
    )


def save_request_database(df):
  try:
    client = get_gspread_client()
    sheet = client.open("Content Database Sosmed").worksheet("Request Konten")

    df_to_save = df.copy()
    df_to_save["Tipe Konten"] = df_to_save["Tipe Konten"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    )

    sheet.clear()
    header = list(df_to_save.columns)
    rows = df_to_save.values.tolist()
    sheet.update([header] + rows)
  except Exception as e:
    st.error(f"Gagal menyimpan ke Google Sheets (Request): {e}")


# Zona waktu WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

# Inisialisasi Session State Database
if "content_db" not in st.session_state:
  st.session_state["content_db"] = load_database()

if "request_db" not in st.session_state:
  st.session_state["request_db"] = load_request_database()

# ==========================================
# SISTEM LOGIN SEDERHANA (USER & PASSWORD)
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
  st.session_state["current_user"] = ""

if not st.session_state["logged_in"]:
  st.markdown("<br><br>", unsafe_allow_html=True)
  col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
  with col_l2:
    with st.container(border=True):
      st.subheader("🔐 Login Aplikasi Sosmed PAS & PTD")
      st.markdown("Silakan masukkan nama dan password Anda untuk masuk.")

      user_credentials = {
          "SURYA": "surya123",
          "SANI": "sani123",
          "REZA": "reza123",
          "GILANG": "gilang123",
          "LARAS": "laras123",
          "EMMA": "emma123",
          "FIAN": "fian123",
      }

      input_user = st.selectbox("Pilih Nama User:", list(user_credentials.keys()))
      input_pass = st.text_input("Password:", type="password")

      if st.button("🚀 Masuk ", type="primary", use_container_width=True):
        if input_pass == user_credentials[input_user]:
          st.session_state["logged_in"] = True
          st.session_state["current_user"] = input_user
          st.success(f"Selamat datang, {input_user}!")
          st.rerun()
        else:
          st.error("Password salah! Silakan coba lagi.")
  
  st.stop()


# ==========================================
# APLIKASI UTAMA (SETELAH LOGIN)
# ==========================================
active_user = st.session_state["current_user"]

st.title("📱 Social Media Content Planner & Scheduler (PAS & PTD)")
st.markdown(
    f"👤 **User Login:** ` {active_user} ` | Kelola jadwal postingan, kategori PAS & PTD, approval, dan reminder."
)

# Tombol Logout di Sidebar
st.sidebar.title("📌 Navigasi Menu")
st.sidebar.markdown(f"👤 Aktif sebagai: **{active_user}**")
if st.sidebar.button("🔒 Logout / Keluar"):
  st.session_state["logged_in"] = False
  st.session_state["current_user"] = ""
  st.rerun()

st.sidebar.markdown("---")

# ==========================================
# HAK AKSES MENU (ROLE-BASED MENU)
# ==========================================
available_menus = []

if active_user in ["LARAS", "FIAN"]:
  available_menus = [
      "📋 Daftar Konten PTD",
      "➕ Tambah Konten Baru",
      "📥 Daftar Request Konten",
      "👔 Approval Konten PTD",
  ]
elif active_user in ["REZA", "GILANG"]:
  available_menus = [
      "📋 Daftar Konten PAS",
      "📋 Daftar Konten PTD",
      "➕ Tambah Konten Baru",
      "📥 Daftar Request Konten",
      "👔 Approval Konten PAS",
      "👔 Approval Konten PTD",
  ]
elif active_user == "EMMA":
  available_menus = [
      "📋 Daftar Konten PAS",
      "➕ Tambah Konten Baru",
      "📥 Daftar Request Konten",
      "👔 Approval Konten PAS",
  ]
else:  # SURYA, SANI (Full Akses)
  available_menus = [
      "📋 Daftar Konten PAS",
      "📋 Daftar Konten PTD",
      "➕ Tambah Konten Baru",
      "📥 Daftar Request Konten",
      "👔 Approval Konten PAS",
      "👔 Approval Konten PTD",
      "🔔 Pusat Notifikasi & History",
      "⏰ Kirim WhatsApp Reminder",
  ]

menu = st.sidebar.radio("Pilih Menu:", available_menus)


# ==========================================
# FUNGSI RENDER TABEL UTAMA (PAS / PTD)
# ==========================================
def render_content_table(kategori_pilih):
  col_title, col_btn = st.columns([4, 1])
  with col_title:
    st.subheader(f"📋 Tabel Jadwal & Manajemen Konten Sosial Media - {kategori_pilih}")
  with col_btn:
    if st.button(f"🔄 Refresh Data", key=f"ref_menu_{kategori_pilih}"):
      st.session_state["content_db"] = load_database()
      for idx, row in st.session_state["content_db"].iterrows():
        w_key = f"stat_status_{row['ID']}"
        if w_key in st.session_state:
          st.session_state[w_key] = row["Status"]
      st.success("Data berhasil diperbarui dari Google Sheets!")
      st.rerun()

  df = st.session_state["content_db"]

  if not df.empty and "Kategori" in df.columns:
    if kategori_pilih == "PAS":
      df = df[(df["Kategori"] == "PAS") | (df["Kategori"] == "") | (df["Kategori"].isna())]
    else:
      df = df[df["Kategori"] == "PTD"]

  if df.empty:
    st.info(
        f"Belum ada konten untuk kategori **{kategori_pilih}**. Silakan tambah"
        " melalui menu **Tambah Konten Baru**."
    )
  else:
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
      filter_status = st.selectbox(
          "Filter Status", ["Semua", "Draft", "Scheduled", "Posted"], key=f"stat_f_{kategori_pilih}"
      )
    with col_f2:
      filter_platform = st.selectbox(
          "Filter Platform", ["Semua", "Instagram", "TikTok", "YouTube", "Facebook"], key=f"plat_f_{kategori_pilih}"
      )
    with col_f3:
      pilih_tanggal = st.date_input(
          "📅 Filter Berdasarkan Tanggal", value=None, key=f"tgl_f_{kategori_pilih}"
      )
    with col_f4:
      search_query = st.text_input(
          "🔍 Cari Judul Konten", placeholder="Ketik kata kunci...", key=f"search_f_{kategori_pilih}"
      )

    filtered_df = df.copy()
    if filter_status != "Semua":
      filtered_df = filtered_df[filtered_df["Status"] == filter_status]
    if filter_platform != "Semua":
      filtered_df = filtered_df[filtered_df["Platform"] == filter_platform]

    if pilih_tanggal:
      tanggal_str = pilih_tanggal.strftime("%Y-%m-%d")
      filtered_df = filtered_df[
          filtered_df["Jadwal Upload"].str.startswith(tanggal_str)
      ]

    if search_query:
      filtered_df = filtered_df[
          filtered_df["Judul Konten"]
          .str.contains(search_query, case=False, na=False)
      ]

    if not filtered_df.empty:
      filtered_df = filtered_df.sort_values(by="Jadwal Upload", ascending=False)

    if filtered_df.empty:
      st.warning("Tidak ada konten yang cocok dengan filter / pencarian.")
    else:
      st.markdown(
          "💡 **Panduan:** Gunakan tombol **✏️ Edit** atau **🗑️ Hapus** di"
          " ujung kanan setiap baris konten."
      )

      for no, (index, row) in enumerate(filtered_df.iterrows(), 1):
        tipe_str = (
            ", ".join(row["Tipe Konten"])
            if isinstance(row["Tipe Konten"], list)
            else str(row["Tipe Konten"])
        )

        with st.container(border=True):
          c1, c2, c3, c4, c5, c6 = st.columns([1.8, 1, 1.2, 1.2, 1.2, 1])

          with c1:
            st.markdown(f"📌 **{no}. {row['Judul Konten']}**")
            app_by_val = row.get('Approved By', '-')
            app_by_info = f" | Approved by: {app_by_val}" if app_by_val and app_by_val != '-' else ""
            st.caption(f"Platform: {row['Platform']} | Tipe: {tipe_str}{app_by_info}")

          with c2:
            st.markdown("🕒 **Status:**")
            status_options = ["Draft", "Scheduled", "Posted"]
            
            widget_key = f"stat_status_{row['ID']}"
            if widget_key not in st.session_state:
              st.session_state[widget_key] = row["Status"]

            def update_status_from_selectbox(r_id=row["ID"], w_key=widget_key):
              val_baru = st.session_state[w_key]
              db_idx = st.session_state["content_db"][
                  st.session_state["content_db"]["ID"] == r_id
              ].index
              if not db_idx.empty:
                st.session_state["content_db"].loc[db_idx, "Status"] = val_baru
                save_database(st.session_state["content_db"])

            st.selectbox(
                "Status",
                status_options,
                key=widget_key,
                on_change=update_status_from_selectbox,
                label_visibility="collapsed",
            )

          with c3:
            st.markdown("📅 **Jadwal:**")
            st.write(row["Jadwal Upload"])

          with c4:
            st.markdown("📂 **GDrive:**")
            if row["Link Google Drive"]:
              st.markdown(f"[Buka Link]({row['Link Google Drive']})")
            else:
              st.write("-")

          with c5:
            st.markdown("📝 **Catatan:**")
            catatan_full = (
                str(row["Catatan"])
                if pd.notna(row["Catatan"]) and row["Catatan"] != ""
                else "-"
            )

            if catatan_full != "-":
              catatan_pendek = (
                  catatan_full[:20] + "..."
                  if len(catatan_full) > 20
                  else catatan_full
              )
              with st.popover(f"📄 {catatan_pendek}"):
                st.markdown("**📋 Salin Catatan / Copywriting:**")
                st.text_area(
                    "Isi Catatan",
                    value=catatan_full,
                    height=150,
                    key=f"txt_area_copy_{row['ID']}",
                    label_visibility="collapsed",
                )
                st.caption(
                    "💡 *Tip:* Tekan lama teks di atas (di HP) atau blok & copy"
                    " (di laptop) untuk menyalin."
                )
            else:
              st.write("-")

          with c6:
            st.markdown("⚡ **Aksi:**")
            col_e, col_d = st.columns(2)
            with col_e:
              if st.button("✏️", key=f"edit_row_{row['ID']}", help="Edit Konten"):
                st.session_state["edit_id"] = row["ID"]
                st.rerun()
            with col_d:
              if st.button("🗑️", key=f"del_row_{row['ID']}", help="Hapus Konten"):
                st.session_state["content_db"] = st.session_state["content_db"][
                    st.session_state["content_db"]["ID"] != row["ID"]
                ]
                save_database(st.session_state["content_db"])
                st.success(f"Konten '{row['Judul Konten']}' berhasil dihapus!")
                st.rerun()

      # FORM EDIT MUNCUL JIKA TOMBOL EDIT DIKLIK
      if "edit_id" in st.session_state and st.session_state["edit_id"]:
        target_id = st.session_state["edit_id"]
        target_row = st.session_state["content_db"][
            st.session_state["content_db"]["ID"] == target_id
        ]

        if not target_row.empty:
          r_data = target_row.iloc[0]
          st.markdown("---")
          st.subheader(f"✏️ Edit Konten: {r_data['Judul Konten']}")

          with st.form("form_edit_konten"):
            edit_kategori = st.selectbox(
                "Pilih Kategori",
                ["PAS", "PTD"],
                index=0 if r_data.get("Kategori", "PAS") in ["PAS", ""] or pd.isna(r_data.get("Kategori")) else 1,
            )
            edit_judul = st.text_input(
                "Judul / Tema Konten", value=r_data["Judul Konten"]
            )

            ec1, ec2 = st.columns(2)
            with ec1:
              platforms_list = ["Instagram", "TikTok", "YouTube", "Facebook"]
              p_idx = (
                  platforms_list.index(r_data["Platform"])
                  if r_data["Platform"] in platforms_list
                  else 0
              )
              edit_platform = st.selectbox(
                  "Platform Utama", platforms_list, index=p_idx
              )

              current_tipe = (
                  r_data["Tipe Konten"]
                  if isinstance(r_data["Tipe Konten"], list)
                  else []
              )
              edit_tipe = st.multiselect(
                  "Tipe Konten",
                  [
                      "IG Feed",
                      "IG Story",
                      "IG Reel",
                      "Carousel",
                      "Video Short",
                      "Lainnya",
                  ],
                  default=current_tipe,
              )
            with ec2:
              try:
                parsed_dt = datetime.strptime(
                    str(r_data["Jadwal Upload"]), "%Y-%m-%d %H:%M"
                )
                def_date = parsed_dt.date()
                def_time = parsed_dt.time()
              except:
                def_date = date.today()
                def_time = datetime.now().time()

              edit_tanggal = st.date_input("Tanggal Upload", value=def_date)
              edit_jam = st.time_input("Jam Upload", value=def_time)

            edit_gdrive = st.text_input(
                "Link Google Drive",
                value=(
                    r_data["Link Google Drive"]
                    if pd.notna(r_data["Link Google Drive"])
                    else ""
                ),
            )

            status_list = ["Draft", "Scheduled", "Posted"]
            s_idx = (
                status_list.index(r_data["Status"])
                if r_data["Status"] in status_list
                else 0
            )
            edit_status = st.selectbox("Status", status_list, index=s_idx)

            edit_catatan = st.text_area(
                "Catatan Tambahan / Copywriting",
                value=(
                    r_data["Catatan"]
                    if pd.notna(r_data["Catatan"]) and r_data["Catatan"] != ""
                    else ""
                ),
            )

            col_submit_e1, col_submit_e2 = st.columns(2)
            with col_submit_e1:
              btn_update = st.form_submit_button(
                  "💾 Update Perubahan", type="primary"
              )
            with col_submit_e2:
              btn_cancel = st.form_submit_button("❌ Batal")

            if btn_update:
              gabung_waktu = datetime.combine(edit_tanggal, edit_jam)

              db_df = st.session_state["content_db"]
              mask = db_df["ID"] == target_id

              db_df.loc[mask, "Kategori"] = edit_kategori
              db_df.loc[mask, "Judul Konten"] = edit_judul
              db_df.loc[mask, "Platform"] = edit_platform
              db_df.at[db_df[mask].index[0], "Tipe Konten"] = edit_tipe
              db_df.loc[mask, "Jadwal Upload"] = gabung_waktu.strftime(
                  "%Y-%m-%d %H:%M"
              )
              db_df.loc[mask, "Link Google Drive"] = edit_gdrive
              db_df.loc[mask, "Status"] = edit_status
              db_df.loc[mask, "Catatan"] = edit_catatan

              save_database(db_df)
              del st.session_state["edit_id"]
              st.success("Perubahan konten berhasil disimpan ke Google Sheets!")
              st.rerun()

            if btn_cancel:
              del st.session_state["edit_id"]
              st.rerun()


# ==========================================
# FUNGSI RENDER APPROVAL (PAS / PTD)
# ==========================================
def render_approval_panel(kategori_approval):
  col_title_app, col_btn_app = st.columns([4, 1])
  with col_title_app:
    st.subheader(f"👔 Panel Persetujuan (Approval) - {kategori_approval}")
  with col_btn_app:
    if st.button(f"🔄 Refresh Data", key=f"ref_app_{kategori_approval}"):
      st.session_state["content_db"] = load_database()
      st.success("Data berhasil diperbarui!")
      st.rerun()

  st.markdown(
      f"Anda login sebagai **{active_user}**. Periksa materi konten **{kategori_approval}**, cek aset Google Drive, dan berikan persetujuan."
  )

  df = st.session_state["content_db"]

  if not df.empty and "Kategori" in df.columns:
    if kategori_approval == "PAS":
      df = df[(df["Kategori"] == "PAS") | (df["Kategori"] == "") | (df["Kategori"].isna())]
    else:
      df = df[df["Kategori"] == "PTD"]

  if df.empty:
    st.info(f"Belum ada data konten untuk kategori {kategori_approval}.")
  else:
    pending_df = df[df["Approval"] == "Pending Approval"].copy()
    if not pending_df.empty:
      pending_df = pending_df.sort_values(by="Jadwal Upload", ascending=False)

    pilih_tgl_app = st.date_input(
        "📅 Filter Tanggal Pengajuan", value=None, key=f"filter_tgl_app_{kategori_approval}"
    )
    if pilih_tgl_app:
      tgl_str = pilih_tgl_app.strftime("%Y-%m-%d")
      pending_df = pending_df[
          pending_df["Jadwal Upload"].str.startswith(tgl_str)
      ]

    st.markdown(f"### ⏳ Konten {kategori_approval} Menunggu Persetujuan (Pending)")
    if pending_df.empty:
      st.success(f"🎉 Tidak ada konten {kategori_approval} yang menunggu approval.")
    else:
      for index, row in pending_df.iterrows():
        tipe_str = (
            ", ".join(row["Tipe Konten"])
            if isinstance(row["Tipe Konten"], list)
            else str(row["Tipe Konten"])
        )

        with st.container(border=True):
          c1, c2, c3, c4, c5 = st.columns([1.8, 1.1, 1.1, 1, 1.5])

          with c1:
            st.markdown(f"📌 **{row['Judul Konten']}**")
            st.caption(f"Platform: {row['Platform']} | Tipe: {tipe_str} | Status: {row['Status']}")

          with c2:
            st.markdown("🕒 **Jadwal:**")
            st.write(row["Jadwal Upload"])

          with c3:
            st.markdown("📂 **GDrive:**")
            if pd.notna(row["Link Google Drive"]) and row["Link Google Drive"]:
              st.markdown(f"[Buka Link]({row['Link Google Drive']})")
            else:
              st.write("-")

          with c4:
            st.markdown("📝 **Catatan:**")
            catatan_full = (
                str(row["Catatan"])
                if pd.notna(row["Catatan"]) and row["Catatan"] != ""
                else "-"
            )
            if catatan_full != "-":
              catatan_pendek = (
                  catatan_full[:25] + "..."
                  if len(catatan_full) > 25
                  else catatan_full
              )
              with st.popover(f"📄 {catatan_pendek}"):
                st.markdown("**Isi Catatan Lengkap:**")
                st.text_area(
                    "Isi Catatan",
                    value=catatan_full,
                    height=120,
                    key=f"txt_app_{row['ID']}",
                    label_visibility="collapsed",
                )
            else:
              st.write("-")

          with c5:
            st.markdown("⚡ **Aksi & Approval:**")
            btn_app, btn_rej = st.columns(2)
            with btn_app:
              if st.button(
                  "✅", key=f"app_{row['ID']}", help="Setujui (Approve)"
              ):
                db_idx = st.session_state["content_db"][
                    st.session_state["content_db"]["ID"] == row["ID"]
                ].index
                st.session_state["content_db"].loc[db_idx, "Approval"] = "Approved"
                st.session_state["content_db"].loc[db_idx, "Approved By"] = active_user
                save_database(st.session_state["content_db"])
                st.success(f"Disetujui oleh {active_user}!")
                st.rerun()
            with btn_rej:
              if st.button("❌", key=f"rej_{row['ID']}", help="Tolak (Reject)"):
                db_idx = st.session_state["content_db"][
                    st.session_state["content_db"]["ID"] == row["ID"]
                ].index
                st.session_state["content_db"].loc[db_idx, "Approval"] = "Rejected"
                st.session_state["content_db"].loc[db_idx, "Approved By"] = f"Rejected by {active_user}"
                save_database(st.session_state["content_db"])
                st.warning(f"Ditolak oleh {active_user}.")
                st.rerun()

          with st.expander(
              f"📲 Kirim Reminder WA untuk: {row['Judul Konten']}"
          ):
            daftar_tim_wa = {
                "Pak Reza": "6281321686233",
                "Bu Emma": "628175731188",
                "Pak Gilang": "6281809830066",
                "Surya": "6281945678904",
                "Bu Laras": "628118490786",
                "Sani": "6288295775828",
                "Pa Fian": "6281383473644",
            }
            pilih_penerima = st.selectbox(
                "Pilih Kontak Penerima WA:",
                list(daftar_tim_wa.keys()),
                key=f"sel_wa_{row['ID']}",
            )
            no_tujuan = st.text_input(
                "Nomor WhatsApp Tujuan:",
                value=daftar_tim_wa[pilih_penerima],
                key=f"no_wa_{row['ID']}",
            )

            try:
              waktu_jadwal = datetime.strptime(
                  str(row["Jadwal Upload"]), "%Y-%m-%d %H:%M"
              ).replace(tzinfo=WIB)
              waktu_sekarang_wib = datetime.now(WIB)
              selisih = waktu_jadwal - waktu_sekarang_wib
              total_d = selisih.total_seconds()
              if total_d > 0:
                j = int(total_d // 3600)
                m = int((total_d % 3600) // 60)
                info_waktu = f"⏳ *Jadwal Tayang:* {row['Jadwal Upload']} WIB (Kurang {j} jam {m} menit lagi)"
              else:
                info_waktu = (
                    f"🚨 *Jadwal Tayang:* {row['Jadwal Upload']} WIB (SUDAH"
                    " LEWAT JADWAL!)"
                )
            except:
              info_waktu = f"🕒 *Jadwal Tayang:* {row['Jadwal Upload']} WIB"

            pesan_approval_wa = (
                f"Halo *{pilih_penerima}*, mohon bantuannya untuk memeriksa dan memberikan approval pada konten sosmed [{kategori_approval}] berikut:\n\n"
                f"📌 *Judul:* {row['Judul Konten']}\n"
                f"📱 *Platform:* {row['Platform']} ({tipe_str})\n"
                f"{info_waktu}\n"
                f"🔗 *Aset GDrive:* {row['Link Google Drive']}\n\n"
                f"Terima kasih!"
            )
            encoded_p_wa = urllib.parse.quote(pesan_approval_wa)
            wa_approval_url = f"https://api.whatsapp.com/send?phone={no_tujuan}&text={encoded_p_wa}"

            st.markdown(
                f'<a href="{wa_approval_url}" target="_blank"><button'
                ' style="background-color:#25D366; color:white; padding:8px'
                ' 16px; border:none; border-radius:5px; cursor:pointer;'
                ' font-size:14px;">📲 Kirim WhatsApp Reminder'
                " Approval</button></a>",
                unsafe_allow_html=True,
            )

    st.markdown(f"### 📜 Riwayat Approval {kategori_approval}")
    cols_to_show = [c for c in ["Judul Konten", "Platform", "Jadwal Upload", "Approval", "Approved By"] if c in df.columns]
    history_approval = df[cols_to_show].copy()
    if not history_approval.empty:
      history_approval = history_approval.sort_values(
          by="Jadwal Upload", ascending=False
      )
    st.dataframe(history_approval, use_container_width=True, hide_index=True)


# ==========================================
# PEMANGGILAN MENU BERDASARKAN HAK AKSES
# ==========================================
if menu == "📋 Daftar Konten PAS":
  render_content_table("PAS")

elif menu == "📋 Daftar Konten PTD":
  render_content_table("PTD")

elif menu == "➕ Tambah Konten Baru":
  st.subheader("➕ Tambah Jadwal Konten & Pilih Kategori (PAS / PTD)")

  with st.form("form_tambah_konten", clear_on_submit=True):
    pilih_kategori_baru = st.selectbox("Pilih Kategori Konten", ["PAS", "PTD"])
    judul = st.text_input("Judul / Tema Konten")
    
    col1, col2 = st.columns(2)
    with col1:
      platform = st.selectbox(
          "Platform Utama", ["Instagram", "TikTok", "YouTube", "Facebook"]
      )
      tipe_konten = st.multiselect(
          "Tipe Konten (Bisa pilih lebih dari satu)",
          [
              "IG Feed",
              "IG Story",
              "IG Reel",
              "Carousel",
              "Video Short",
              "Lainnya",
          ],
      )
    with col2:
      tanggal_upload = st.date_input("Tanggal Upload")
      jam_upload = st.time_input("Jam Upload")

    link_gdrive = st.text_input(
        "Link Google Drive (Aset Foto/Video/Caption)"
    )
    
    status = st.selectbox(
        "Status Awal",
        ["Draft", "Scheduled"],
        index=0,
        help="Pilih 'Draft' jika ingin diajukan terlebih dahulu untuk menunggu Approval.",
    )
    
    catatan = st.text_area("Catatan Tambahan / Copywriting")

    submit_button = st.form_submit_button("Simpan Jadwal Konten")

    if submit_button:
      if judul and link_gdrive and tipe_konten:
        st.session_state["content_db"] = load_database()

        waktu_gabung = datetime.combine(tanggal_upload, jam_upload)
        new_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

        new_data = {
            "ID": new_id,
            "Kategori": pilih_kategori_baru,
            "Judul Konten": judul,
            "Platform": platform,
            "Tipe Konten": tipe_konten,
            "Jadwal Upload": waktu_gabung.strftime("%Y-%m-%d %H:%M"),
            "Link Google Drive": link_gdrive,
            "Status": status,
            "Approval": "Pending Approval",
            "Approved By": "-",
            "Catatan": catatan,
        }

        st.session_state["content_db"] = pd.concat(
            [
                st.session_state["content_db"],
                pd.DataFrame([new_data]),
            ],
            ignore_index=True,
        )
        save_database(st.session_state["content_db"])
        st.success(
            f"Berhasil! Konten kategori **{pilih_kategori_baru}** dengan status **{status}** tersimpan di Google Sheets."
        )
      else:
        st.warning(
            "Mohon isi Judul, Link Google Drive, dan minimal pilih satu Tipe Konten."
        )

elif menu == "📥 Daftar Request Konten":
  st.subheader("📥 Daftar & Form Request Konten Baru (PAS & PTD)")
  st.markdown("Menu khusus untuk mengajukan atau merekap usulan/ide request konten baru tanpa masuk ke jadwal utama.")

  tab_req_list, tab_req_form = st.tabs(["📋 Rekapan Request Konten", "➕ Buat Request Baru"])

  with tab_req_form:
    st.markdown("### Form Pengajuan Request Konten")
    with st.form("form_request_konten", clear_on_submit=True):
      req_kategori = st.selectbox("Pilih Kategori", ["PAS", "PTD"], key="req_kat")
      req_judul = st.text_input("Judul / Topik Usulan Konten", key="req_jdl")
      
      rc1, rc2 = st.columns(2)
      with rc1:
        req_platform = st.selectbox(
            "Target Platform", ["Instagram", "TikTok", "YouTube", "Facebook"], key="req_plt"
        )
        req_tipe = st.multiselect(
            "Format / Tipe Konten",
            [
                "IG Feed",
                "IG Story",
                "IG Reel",
                "Carousel",
                "Video Short",
                "Lainnya",
            ],
            key="req_tp"
        )
      with rc2:
        req_status = st.selectbox(
            "Status Usulan", ["Menunggu Review", "Disetujui", "Ditolak"], key="req_sts"
        )
        req_link = st.text_input("Link Referensi / Dokumen Pendukung (Opsional)", key="req_lnk")

      req_catatan = st.text_area("Catatan / Penjelasan Detail Ide Request", key="req_ctt")

      submit_req = st.form_submit_button("📩 Kirim Usulan Request")

      if submit_req:
        if req_judul and req_tipe:
          st.session_state["request_db"] = load_request_database()
          req_id = datetime.now().strftime("%Y%m%d%H%M%S%f")

          new_req_data = {
              "ID": req_id,
              "Kategori": req_kategori,
              "Judul Request": req_judul,
              "Platform": req_platform,
              "Tipe Konten": req_tipe,
              "Pengaju": active_user,
              "Link Referensi": req_link if req_link else "-",
              "Status Request": req_status,
              "Catatan": req_catatan,
          }

          st.session_state["request_db"] = pd.concat(
              [
                  st.session_state["request_db"],
                  pd.DataFrame([new_req_data]),
              ],
              ignore_index=True,
          )
          save_request_database(st.session_state["request_db"])
          st.success(f"Berhasil! Usulan request konten kategori **{req_kategori}** berhasil disimpan.")
          st.rerun()
        else:
          st.warning("Mohon isi Judul Usulan dan minimal pilih satu Tipe Konten.")

  with tab_req_list:
    st.markdown("### Rekapan Data Request Konten")
    
    if st.button("🔄 Refresh Data Request"):
      st.session_state["request_db"] = load_request_database()
      st.success("Data request berhasil diperbarui!")
      st.rerun()

    req_df = st.session_state["request_db"]

    if req_df.empty:
      st.info("Belum ada data request konten yang dimasukkan.")
    else:
      filter_kat_req = st.selectbox("Filter Berdasarkan Kategori", ["Semua", "PAS", "PTD"], key="f_kat_req")
      
      filtered_req = req_df.copy()
      if filter_kat_req != "Semua":
        filtered_req = filtered_req[filtered_req["Kategori"] == filter_kat_req]

      if filtered_req.empty:
        st.warning(f"Tidak ada request untuk kategori {filter_kat_req}.")
      else:
        for idx, r_row in filtered_req.iterrows():
          t_str = (
              ", ".join(r_row["Tipe Konten"])
              if isinstance(r_row["Tipe Konten"], list)
              else str(r_row["Tipe Konten"])
          )
          
          with st.container(border=True):
            rc_col1, rc_col2, rc_col3, rc_col4 = st.columns([2, 1.2, 1.2, 1])
            with rc_col1:
              st.markdown(f"📌 **[{r_row['Kategori']}] {r_row['Judul Request']}**")
              st.caption(f"Platform: {r_row['Platform']} | Format: {t_str} | Diajukan oleh: **{r_row['Pengaju']}**")
            with rc_col2:
              st.markdown("📋 **Status:**")
              st.write(f"` {r_row['Status Request']} `")
            with rc_col3:
              st.markdown("🔗 **Referensi:**")
              if r_row["Link Referensi"] and r_row["Link Referensi"] != "-":
                st.markdown(f"[Buka Link]({r_row['Link Referensi']})")
              else:
                st.write("-")
            with rc_col4:
              st.markdown("⚡ **Aksi:**")
              if st.button("🗑️ Hapus", key=f"del_req_{r_row['ID']}"):
                st.session_state["request_db"] = st.session_state["request_db"][
                    st.session_state["request_db"]["ID"] != r_row["ID"]
                ]
                save_request_database(st.session_state["request_db"])
                st.success("Request berhasil dihapus!")
                st.rerun()

            if r_row["Catatan"] and r_row["Catatan"] != "-":
              with st.expander("📝 Lihat Detail / Catatan Request"):
                st.info(r_row["Catatan"])

elif menu == "👔 Approval Konten PAS":
  render_approval_panel("PAS")

elif menu == "👔 Approval Konten PTD":
  render_approval_panel("PTD")

elif menu == "🔔 Pusat Notifikasi & History":
  col_title_notif, col_btn_notif = st.columns([4, 1])
  with col_title_notif:
    st.subheader("🔔 Pusat Notifikasi & Riwayat Konten")
  with col_btn_notif:
    if st.button("🔄 Refresh Data", key="ref_menu4"):
      st.session_state["content_db"] = load_database()
      st.success("Data berhasil diperbarui!")
      st.rerun()

  df = st.session_state["content_db"]

  if df.empty:
    st.info("Belum ada data konten atau riwayat aktivitas.")
  else:
    tab_notif, tab_history = st.tabs(
        ["🚨 Notifikasi Mendesak (H-2 Jam)", "📜 Riwayat & History Lengkap"]
    )

    with tab_notif:
      scheduled_df = df[
          (df["Status"] == "Scheduled") & (df["Approval"] == "Approved")
      ].copy()
      if scheduled_df.empty:
        st.success(
            "🎉 Tidak ada peringatan mendesak untuk konten yang sudah di-approve."
        )
      else:
        ada_alert = False

        scheduled_df = scheduled_df.sort_values(
            by="Jadwal Upload", ascending=True
        )

        for index, row in scheduled_df.iterrows():
          try:
            waktu_jadwal = datetime.strptime(
                str(row["Jadwal Upload"]), "%Y-%m-%d %H:%M"
            ).replace(tzinfo=WIB)
            waktu_sekarang_wib = datetime.now(WIB)
          except:
            continue

          selisih_waktu = waktu_jadwal - waktu_sekarang_wib
          total_detik = selisih_waktu.total_seconds()
          sisa_menit = total_detik / 60

          if sisa_menit <= 120 and total_detik >= -720 * 60:
            ada_alert = True
            tipe_str = (
                ", ".join(row["Tipe Konten"])
                if isinstance(row["Tipe Konten"], list)
                else str(row["Tipe Konten"])
            )
            kat_label = row.get("Kategori", "PAS")
            if not kat_label or kat_label == "":
              kat_label = "PAS"

            if total_detik > 0:
              jam_cd = int(total_detik // 3600)
              menit_cd = int((total_detik % 3600) // 60)
              detik_cd = int(total_detik % 60)
              countdown_text = f"⏳ **Countdown:** {jam_cd:02d} jam {menit_cd:02d} menit {detik_cd:02d} detik lagi menuju jam H"
            else:
              countdown_text = (
                  "🚨 **STATUS:** Waktu upload sudah lewat dari jadwal dan belum diubah ke 'Posted'!"
              )

            st.error(
                f"🚨 **PERINGATAN UPLOAD DEKAT!**\n\n"
                f"• **Kategori & Judul:** [{kat_label}] {row['Judul Konten']}\n"
                f"• **Platform & Format:** {row['Platform']} ({tipe_str})\n"
                f"• **Jadwal Target:** {row['Jadwal Upload']} WIB\n"
                f"• {countdown_text}"
            )
            if pd.notna(row["Link Google Drive"]):
              st.markdown(
                  f"🔗 [📂 Buka Aset di Google Drive]({row['Link Google Drive']})"
              )
            st.divider()

        if not ada_alert:
          st.info(
              "ℹ️ Belum ada konten approved yang masuk dalam rentang H-2 jam menuju waktu upload."
          )

    with tab_history:
      st.markdown("### 📊 Statistik & Riwayat Seluruh Konten")

      pilih_tgl_hist = st.date_input(
          "📅 Filter Tanggal Riwayat", value=None, key="filter_tgl_hist"
      )
      hist_df = df.copy()
      if pilih_tgl_hist:
        tgl_hist_str = pilih_tgl_hist.strftime("%Y-%m-%d")
        hist_df = hist_df[
            hist_df["Jadwal Upload"].str.startswith(tgl_hist_str)
        ]

      if not hist_df.empty:
        hist_df = hist_df.sort_values(by="Jadwal Upload", ascending=False)

      total_konten = len(hist_df)
      total_posted = len(hist_df[hist_df["Status"] == "Posted"])
      total_scheduled = len(hist_df[hist_df["Status"] == "Scheduled"])
      total_draft = len(hist_df[hist_df["Status"] == "Draft"])

      col_s1, col_s2, col_s3, col_s4 = st.columns(4)
      col_s1.metric("Total Konten", total_konten)
      col_s2.metric("Sudah Posted", total_posted)
      col_s3.metric("Terjadwal", total_scheduled)
      col_s4.metric("Draft", total_draft)

      st.markdown("<br>", unsafe_allow_html=True)
      history_display = hist_df.copy()
      history_display["Tipe Konten"] = history_display["Tipe Konten"].apply(
          lambda x: ", ".join(x) if isinstance(x, list) else str(x)
      )
      
      cols_history_show = [c for c in ["Kategori", "Judul Konten", "Platform", "Tipe Konten", "Approval", "Approved By", "Status", "Jadwal Upload", "Catatan"] if c in history_display.columns]
      st.dataframe(
          history_display[cols_history_show],
          use_container_width=True,
          hide_index=True,
      )

elif menu == "⏰ Kirim WhatsApp Reminder":
  st.subheader("📲 Kirim Peringatan Cepat ke WhatsApp Tim")
  st.markdown(
      "Pilih konten yang mau diingatkan, lalu pilih nama / nomor WhatsApp anggota tim tujuan."
  )

  df = st.session_state["content_db"]
  scheduled_df = df[df["Status"] == "Scheduled"]

  if scheduled_df.empty:
    st.info("Tidak ada konten dengan status 'Scheduled' untuk diingatkan.")
  else:
    pilihan_konten = st.selectbox(
        "Pilih Konten yang Mau Diingatkan",
        scheduled_df["Judul Konten"].tolist(),
    )
    selected_row = scheduled_df[
        scheduled_df["Judul Konten"] == pilihan_konten
    ].iloc[0]

    daftar_tim = {
        "Pak Reza": "6281321686233",
        "Bu Emma": "628175731188",
        "Pak Gilang": "6281809830066",
        "Surya": "6281945678904",
        "Bu Laras": "628118490786",
        "Sani": "6288295775828",
        "Pa Fian": "6281383473644",
    }

    pilihan_admin = st.selectbox(
        "Pilih Anggota Tim Tujuan WhatsApp:", list(daftar_tim.keys())
    )
    nomor_tujuan = daftar_tim[pilihan_admin]

    nomor_final = st.text_input(
        "Nomor WhatsApp Tujuan (Format 62...):", value=nomor_tujuan
    )

    tipe_str = (
        ", ".join(selected_row["Tipe Konten"])
        if isinstance(selected_row["Tipe Konten"], list)
        else str(selected_row["Tipe Konten"])
    )
    kat_label = selected_row.get("Kategori", "PAS")
    if not kat_label or kat_label == "":
      kat_label = "PAS"

    pesan_wa = (
        f"Halo! Reminder nih, konten sosial media *[{kat_label}] {selected_row['Judul Konten']}* "
        f"dengan format ({tipe_str}) harus naik ke {selected_row['Platform']} "
        f"pada jam {selected_row['Jadwal Upload']} WIB. Jangan lupa cek asetnya ya: {selected_row['Link Google Drive']}"
    )

    encoded_pesan = urllib.parse.quote(pesan_wa)
    whatsapp_url = (
        f"https://api.whatsapp.com/send?phone={nomor_final}&text={encoded_pesan}"
    )

    st.markdown(
        f'<a href="{whatsapp_url}" target="_blank"><button'
        ' style="background-color:#25D366; color:white; padding:10px'
        ' 20px; border:none; border-radius:5px; cursor:pointer; font-size:16px;">📲'
        " Buka WhatsApp & Kirim Pesan</button></a>",
        unsafe_allow_html=True,
    )