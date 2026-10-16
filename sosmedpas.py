from datetime import datetime
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
    "Kelola jadwal postingan, tabel interaktif rapi, dan Approval Direksi."
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
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
      filter_status = st.selectbox(
          "Filter Status", ["Semua", "Draft", "Scheduled", "Posted"]
      )
    with col_f2:
      filter_platform = st.selectbox(
          "Filter Platform", ["Semua", "Instagram", "TikTok", "YouTube", "Facebook"]
      )
    with col_f3:
      search_query = st.text_input(
          "🔍 Cari Judul Konten", placeholder="Ketik kata kunci..."
      )

    filtered_df = df.copy()
    if filter_status != "Semua":
      filtered_df = filtered_df[filtered_df["Status"] == filter_status]
    if filter_platform != "Semua":
      filtered_df = filtered_df[filtered_df["Platform"] == filter_platform]
    if search_query:
      filtered_df = filtered_df[
          filtered_df["Judul Konten"]
          .str.contains(search_query, case=False, na=False)
      ]

    if filtered_df.empty:
      st.warning("Tidak ada konten yang cocok dengan filter / pencarian.")
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

    st.subheader("📥 Backup Data ke CSV (Bisa dibuka di Excel)")


    def convert_df_to_csv(df_to_export):
      export_data = df_to_export.copy()
      export_data["Tipe Konten"] = export_data["Tipe Konten"].apply(
          lambda x: ", ".join(x) if isinstance(x, list) else x
      )
      return export_data.to_csv(index=False).encode("utf-8")


    csv_file = convert_df_to_csv(df)
    st.download_button(
        label="📥 Download Backup (.csv)",
        data=csv_file,
        file_name=f"Backup_Jadwal_Sosmed_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )

# ==========================================
# MENU 2: TAMBAH KONTEN BARU
# ==========================================
elif menu == "➕ Tambah Konten Baru":
  st.subheader("➕ Tambah Jadwal Konten & Link Google Drive")

  with st.form("form_tambah_konten", clear_on_submit=True):
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
    status = st.selectbox("Status Awal", ["Draft", "Scheduled"])
    catatan = st.text_area("Catatan Tambahan / Copywriting")

    submit_button = st.form_submit_button("Simpan Jadwal Konten")

    if submit_button:
      if judul and link_gdrive and tipe_konten:
        waktu_gabung = datetime.combine(tanggal_upload, jam_upload)
        new_id = datetime.now().strftime("%Y%m%d%H%M%S")

        new_data = {
            "ID": new_id,
            "Judul Konten": judul,
            "Platform": platform,
            "Tipe Konten": tipe_konten,
            "Jadwal Upload": waktu_gabung.strftime("%Y-%m-%d %H:%M"),
            "Link Google Drive": link_gdrive,
            "Status": status,
            "Approval": "Pending Approval",
            "Catatan": catatan,
        }

        st.session_state["content_db"] = pd.concat(
            [
                st.session_state["content_db"],
                pd.DataFrame([new_data]),
            ],
            ignore_index=True,
        )
        st.success(
            "Berhasil! Konten baru diajukan dan menunggu Approval Direksi."
        )
      else:
        st.warning(
            "Mohon isi Judul, Link Google Drive, dan minimal pilih satu Tipe"
            " Konten."
        )

# ==========================================
# MENU 3: APPROVAL DIREKSI (Dibuat Tabel Rapi)
# ==========================================
elif menu == "👔 Approval Direksi":
  st.subheader("👔 Panel Persetujuan (Approval) Direksi")
  st.markdown(
      "Direksi dapat memeriksa materi konten, mengecek aset Google Drive, dan"
      " memberikan persetujuan."
  )

  df = st.session_state["content_db"]

  if df.empty:
    st.info("Belum ada konten yang diajukan.")
  else:
    pending_df = df[df["Approval"] == "Pending Approval"].copy()

    st.markdown("### ⏳ Konten Menunggu Persetujuan")
    if pending_df.empty:
      st.success("🎉 Tidak ada konten yang menunggu approval saat ini.")
    else:
      st.markdown(
          "💡 **Cara Approval:** Ubah kolom **Pilih Aksi** menjadi"
          " `Approved` atau `Rejected`, lalu klik tombol **Simpan Keputusan"
          " Direksi** di bawah tabel."
      )

      pending_df["Tipe Konten"] = pending_df["Tipe Konten"].apply(
          lambda x: ", ".join(x) if isinstance(x, list) else x
      )
      pending_df["Pilih Aksi"] = (
          "Pending"  # Kolom pilihan untuk direksi di tabel
      )

      edited_approval = st.data_editor(
          pending_df[
              [
                  "ID",
                  "Judul Konten",
                  "Platform",
                  "Tipe Konten",
                  "Jadwal Upload",
                  "Link Google Drive",
                  "Catatan",
                  "Pilih Aksi",
              ]
          ],
          column_config={
              "ID": None,
              "Link Google Drive": st.column_config.LinkColumn(
                  "Link Google Drive",
                  help="Klik untuk membuka folder/file di GDrive",
                  display_text="📂 Buka GDrive",
              ),
              "Pilih Aksi": st.column_config.SelectboxColumn(
                  "Pilih Aksi",
                  options=["Pending", "Approved", "Rejected"],
                  required=True,
              ),
          },
          disabled=[
              "Judul Konten",
              "Platform",
              "Tipe Konten",
              "Jadwal Upload",
              "Link Google Drive",
              "Catatan",
          ],
          use_container_width=True,
          hide_index=True,
          key="approval_table_editor",
      )

      if st.button("💾 Simpan Keputusan Direksi", type="primary"):
        for index, row in edited_approval.iterrows():
          row_id = row["ID"]
          aksi = row["Pilih Aksi"]

          if aksi != "Pending":
            st.session_state["content_db"].loc[
                st.session_state["content_db"]["ID"] == row_id, "Approval"
            ] = aksi

        st.success("Keputusan approval berhasil disimpan!")
        st.rerun()

    st.markdown("### 📜 Riwayat Semua Approval")
    history_approval = df[
        ["Judul Konten", "Platform", "Jadwal Upload", "Approval"]
    ].copy()
    st.dataframe(history_approval, use_container_width=True, hide_index=True)

# ==========================================
# MENU 4: PUSAT NOTIFIKASI & HISTORY
# ==========================================
elif menu == "🔔 Pusat Notifikasi & History":
  st.subheader("🔔 Pusat Notifikasi & Riwayat Konten")
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
            "🎉 Tidak ada peringatan mendesak untuk konten yang sudah"
            " di-approve."
        )
      else:
        waktu_sekarang = datetime.now()
        ada_alert = False

        for index, row in scheduled_df.iterrows():
          waktu_jadwal = datetime.strptime(
              row["Jadwal Upload"], "%Y-%m-%d %H:%M"
          )
          selisih_waktu = waktu_jadwal - waktu_sekarang
          total_detik = selisih_waktu.total_seconds()
          sisa_menit = total_detik / 60

          if sisa_menit <= 120:
            ada_alert = True
            tipe_str = (
                ", ".join(row["Tipe Konten"])
                if isinstance(row["Tipe Konten"], list)
                else row["Tipe Konten"]
            )

            if total_detik > 0:
              jam_cd = int(total_detik // 3600)
              menit_cd = int((total_detik % 3600) // 60)
              detik_cd = int(total_detik % 60)
              countdown_text = f"⏳ **Countdown:** {jam_cd:02d} jam {menit_cd:02d} menit {detik_cd:02d} detik lagi"
            else:
              countdown_text = (
                  "🚨 **STATUS:** Waktu upload sudah lewat dari jadwal!"
              )

            st.error(
                f"🚨 **PERINGATAN UPLOAD DEKAT!**\n\n"
                f"• **Judul:** {row['Judul Konten']}\n"
                f"• **Platform & Format:** {row['Platform']} ({tipe_str})\n"
                f"• **Jadwal Target:** {row['Jadwal Upload']}\n"
                f"• {countdown_text}"
            )
            st.markdown(
                f"🔗 [📂 Buka Aset di Google"
                f" Drive]({row['Link Google Drive']})"
            )
            st.divider()

        if not ada_alert:
          st.info(
              "ℹ️ Belum ada konten approved yang masuk masa H-2 jam dari"
              " sekarang."
          )

    with tab_history:
      st.markdown("### 📊 Statistik & Riwayat Seluruh Konten")
      total_konten = len(df)
      total_posted = len(df[df["Status"] == "Posted"])
      total_scheduled = len(df[df["Status"] == "Scheduled"])
      total_draft = len(df[df["Status"] == "Draft"])

      col_s1, col_s2, col_s3, col_s4 = st.columns(4)
      col_s1.metric("Total Konten", total_konten)
      col_s2.metric("Sudah Posted", total_posted)
      col_s3.metric