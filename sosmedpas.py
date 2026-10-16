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
    "Kelola jadwal postingan, link Google Drive interaktif, dan Approval"
    " Direksi."
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
          "Daftar seluruh konten beserta link Google Drive dan tombol aksi"
          " langsung:"
      )

      # Header Kolom Kustom untuk Tabel Manajemen
      col_h1, col_h2, col_h3, col_h4, col_h5, col_h6, col_h7, col_h8 = st.columns(
          [2, 1.2, 1.5, 1.5, 1, 1.2, 1.2, 1.2]
      )
      col_h1.markdown("**Judul**")
      col_h2.markdown("**Platform**")
      col_h3.markdown("**Tipe**")
      col_h4.markdown("**Jadwal**")
      col_h5.markdown("**Status**")
      col_h6.markdown("**Approval**")
      col_h7.markdown("**GDrive**")
      col_h8.markdown("**Aksi**")
      st.divider()

      for index, row in filtered_df.iterrows():
        tipe_str = (
            ", ".join(row["Tipe Konten"])
            if isinstance(row["Tipe Konten"], list)
            else row["Tipe Konten"]
        )

        c_r1, c_r2, c_r3, c_r4, c_r5, c_r6, c_r7, c_r8 = st.columns(
            [2, 1.2, 1.5, 1.5, 1, 1.2, 1.2, 1.2]
        )

        c_r1.write(row["Judul Konten"])
        c_r2.write(row["Platform"])
        c_r3.write(tipe_str)
        c_r4.write(row["Jadwal Upload"])
        c_r5.write(row["Status"])
        c_r6.write(row["Approval"])

        if row["Link Google Drive"]:
          c_r7.markdown(f"[📂 Buka]({row['Link Google Drive']})")
        else:
          c_r7.write("-")

        # Tombol Aksi per Baris (Post & Hapus disatukan rapi di kolom terakhir)
        with c_r8:
          sub_c1, sub_c2 = st.columns(2)
          with sub_c1:
            if st.button("✅", key=f"post_{row['ID']}", help="Tandai Posted"):
              st.session_state["content_db"].loc[
                  st.session_state["content_db"]["ID"] == row["ID"], "Status"
              ] = "Posted"
              st.rerun()
          with sub_c2:
            if st.button("🗑️", key=f"del_{row['ID']}", help="Hapus Konten"):
              st.session_state["content_db"] = st.session_state["content_db"][
                  st.session_state["content_db"]["ID"] != row["ID"]
              ]
              st.rerun()

        st.markdown(
            "<hr style='margin: 5px 0px; opacity: 0.2;'>", unsafe_allow_html=True
        )

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
# MENU 3: APPROVAL DIREKSI
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
    pending_df = df[df["Approval"] == "Pending Approval"]

    st.markdown("### ⏳ Konten Menunggu Persetujuan")
    if pending_df.empty:
      st.success("🎉 Tidak ada konten yang menunggu approval saat ini.")
    else:
      for index, row in pending_df.iterrows():
        tipe_str = (
            ", ".join(row["Tipe Konten"])
            if isinstance(row["Tipe Konten"], list)
            else row["Tipe Konten"]
        )
        with st.container():
          st.markdown(f"### 📌 {row['Judul Konten']}")
          c1, c2, c3 = st.columns(3)
          c1.write(f"**Platform:** {row['Platform']} ({tipe_str})")
          c2.write(f"**Jadwal:** {row['Jadwal Upload']}")
          c3.write(f"**Status Saat Ini:** {row['Approval']}")

          if row["Link Google Drive"]:
            st.markdown(
                f"🔗 [📂 Buka Aset di Google Drive]({row['Link Google Drive']})"
            )
          if row["Catatan"]:
            st.info(f"**Catatan/Copywriting:** {row['Catatan']}")

          col_ap1, col_ap2, col_ap3 = st.columns([1, 1, 4])
          if col_ap1.button("✅ Approve", key=f"app_{row['ID']}"):
            st.session_state["content_db"].loc[
                st.session_state["content_db"]["ID"] == row["ID"], "Approval"
            ] = "Approved"
            st.success(f"Konten '{row['Judul Konten']}' berhasil disetujui!")
            st.rerun()
          if col_ap2.button("❌ Reject", key=f"rej_{row['ID']}"):
            st.session_state["content_db"].loc[
                st.session_state["content_db"]["ID"] == row["ID"], "Approval"
            ] = "Rejected"
            st.warning(f"Konten '{row['Judul Konten']}' ditolak.")
            st.rerun()
          st.divider()

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