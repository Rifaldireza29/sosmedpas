from datetime import date, datetime
import io
import urllib.parse
import pandas as pd
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Social Media Planner & Scheduler", page_icon="📱", layout="wide"
)

# Inisialisasi Database Sementara di Session State
if "content_db" not in st.session_state:
  st.session_state["content_db"] = pd.DataFrame(
      columns=[
          "ID",
          "Judul Konten",
          "Platform",
          "Tipe Konten",
          "Jadwal Upload",
          "Link Google Drive",
          "Status",
          "Approval",
          "Catatan",
      ]
  )

# PENGAMAN: Jika membuka aplikasi dan kolom 'Approval' belum ada di data lama
if "Approval" not in st.session_state["content_db"].columns:
  st.session_state["content_db"]["Approval"] = "Pending Approval"

st.title("📱 Social Media Content Planner & Scheduler")
st.markdown(
    "Kelola jadwal postingan, tabel interaktif rapi, filter tanggal, dan"
    " Approval Direksi."
)

# Sidebar untuk Navigasi Menu
menu = st.sidebar.selectbox(
    "Pilih Menu",
    [
        "📋 Daftar Konten & Jadwal",
        "➕ Tambah Konten Baru",
        "👔 Approval Direksi",
        "🔔 Pusat Notifikasi & History",
        "⏰ Kirim WhatsApp Reminder",
    ],
)

# ==========================================
# MENU 1: DAFTAR KONTEN & JADWAL
# ==========================================
if menu == "📋 Daftar Konten & Jadwal":
  st.subheader("📋 Tabel Jadwal & Manajemen Konten Sosial Media")

  df = st.session_state["content_db"]

  if df.empty:
    st.info(
        "Belum ada konten yang dijadwalkan. Silakan tambah melalui menu **Tambah"
        " Konten Baru**."
    )
  else:
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
      filter_status = st.selectbox(
          "Filter Status", ["Semua", "Draft", "Scheduled", "Posted"]
      )
    with col_f2:
      filter_platform = st.selectbox(
          "Filter Platform", ["Semua", "Instagram", "TikTok", "YouTube", "Facebook"]
      )
    with col_f3:
      pilih_tanggal = st.date_input(
          "📅 Filter Berdasarkan Tanggal", value=None
      )
    with col_f4:
      search_query = st.text_input(
          "🔍 Cari Judul Konten", placeholder="Ketik kata kunci..."
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

    if filtered_df.empty:
      st.warning("Tidak ada konten yang cocok dengan filter / pencarian tanggal.")
    else:
      st.markdown(
          "💡 **Cara Kelola:** Ubah kolom **Status** (Draft/Scheduled/Posted) atau"
          " centang kolom **Hapus?**, lalu klik tombol **Simpan Perubahan** di"
          " bawah tabel."
      )

      edit_df = filtered_df.copy()
      edit_df["Tipe Konten"] = edit_df["Tipe Konten"].apply(
          lambda x: ", ".join(x) if isinstance(x, list) else x
      )
      edit_df["Hapus?"] = False

      edited_df = st.data_editor(
          edit_df[
              [
                  "ID",
                  "Judul Konten",
                  "Platform",
                  "Tipe Konten",
                  "Jadwal Upload",
                  "Status",
                  "Approval",
                  "Link Google Drive",
                  "Hapus?",
              ]
          ],
          column_config={
              "ID": None,
              "Status": st.column_config.SelectboxColumn(
                  "Status",
                  options=["Draft", "Scheduled", "Posted"],
                  required=True,
              ),
              "Link Google Drive": st.column_config.LinkColumn(
                  "Link Google Drive",
                  help="Klik untuk membuka folder/file di GDrive",
                  display_text="📂 Buka GDrive",
              ),
              "Hapus?": st.column_config.CheckboxColumn(
                  "Hapus?", default=False
              ),
          },
          disabled=[
              "Judul Konten",
              "Platform",
              "Tipe Konten",
              "Jadwal Upload",
              "Approval",
              "Link Google Drive",
          ],
          use_container_width=True,
          hide_index=True,
          key="manager_table_editor",
      )

      if st.button("💾 Simpan Perubahan Tabel", type="primary"):
        for index, row in edited_df.iterrows():
          row_id = row["ID"]
          new_status = row["Status"]
          is_deleted = row["Hapus?"]

          if is_deleted:
            st.session_state["content_db"] = st.session_state["content_db"][
                st.session_state["content_db"]["ID"] != row_id
            ]
          else:
            st.session_state["content_db"].loc[
                st.session_state["content_db"]["ID"] == row_id, "Status"
            ] = new_status

        st.success("Perubahan berhasil disimpan!")
        st.rerun()

    st.divider()