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
  st.subheader("📋 Tabel Jadwal & Status Konten Sosial Media")

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
      display_df = filtered_df.copy()
      display_df["Tipe Konten"] = display_df["Tipe Konten"].apply(
          lambda x: ", ".join(x) if isinstance(x, list) else x
      )

      # Tampilkan tabel interaktif utama
      st.dataframe(
          display_df[
              [
                  "Judul Konten",
                  "Platform",
                  "Tipe Konten",
                  "Jadwal Upload",
                  "Status",
                  "Approval",
                  "Link Google Drive",
                  "Catatan",
              ]
          ],
          column_config={
              "Link Google Drive": st.column_config.LinkColumn(
                  "Link Google Drive",
                  help="Klik untuk membuka folder/file di GDrive",
                  display_text="📂 Buka GDrive",
              )
          },
          use_container_width=True,
          hide_index=True,
      )

      st.markdown("### ⚙️ Aksi Cepat Kelola Konten")
      st.markdown(
          "Ubah status menjadi 'Posted' atau hapus konten langsung dari daftar"
          " di bawah:"
      )

      # Tampilan list per baris dengan tombol aksi di sebelah kanan
      for index, row in filtered_df.iterrows():
        tipe_str = (
            ", ".join(row["Tipe Konten"])
            if isinstance(row["Tipe Konten"], list)
            else row["Tipe Konten"]
        )

        col_info, col_btn1, col_btn2 = st.columns([6, 1.2, 1.2])

        with col_info:
          st.markdown(
              f"**📌 {row['Judul Konten']}** | *{row['Platform']} ({tipe_str})*"
              f" | ⏰ {row['Jadwal Upload']} | Status: `{row['Status']}` |"
              f" Approval: `{row['Approval']}`"
          )

        with col_btn1:
          if st.button("✅ Post", key=f"post_{row['ID']}"):
            st.session_state["content_db"].loc[
                st.session_state["content_db"]["ID"] == row["ID"], "Status"
            ] = "Posted"
            st.rerun()

        with col_btn2:
          if st.button("🗑️ Hapus", key=f"del_{row['ID']}"):
            st.session_state["content_db"] = st.session_state["content_db"][
                st.session_state["content_db"]["ID"] != row["ID"]
            ]
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
      total_konten = len(df)
      total_posted = len(df[df["Status"] == "Posted"])
      total_scheduled = len(df[df["Status"] == "Scheduled"])
      total_draft = len(df[df["Status"] == "Draft"])

      col_s1, col_s2, col_s3, col_s4 = st.columns(4)
      col_s1.metric("Total Konten", total_konten)
      col_s2.metric("Sudah Posted", total_posted)
      col_s3.metric("Terjadwal", total_scheduled)
      col_s4.metric("Draft", total_draft)

      st.markdown("<br>", unsafe_allow_html=True)
      history_display = df.copy()
      history_display["Tipe Konten"] = history_display["Tipe Konten"].apply(
          lambda x: ", ".join(x) if isinstance(x, list) else x
      )
      st.dataframe(
          history_display[
              [
                  "Judul Konten",
                  "Platform",
                  "Tipe Konten",
                  "Approval",
                  "Status",
              ]
          ],
          use_container_width=True,
          hide_index=True,
      )

# ==========================================
# MENU 5: KIRIM WHATSAPP REMINDER
# ==========================================
elif menu == "⏰ Kirim WhatsApp Reminder":
  st.subheader("📲 Kirim Peringatan Cepat ke WhatsApp")
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

    nomor_tujuan = st.text_input(
        "Nomor WhatsApp Admin (awali 62, contoh: 62812345678):",
        value="6281234567890",
    )

    tipe_str = (
        ", ".join(selected_row["Tipe Konten"])
        if isinstance(selected_row["Tipe Konten"], list)
        else selected_row["Tipe Konten"]
    )
    pesan_wa = (
        f"Halo! Reminder nih, konten sosial media *{selected_row['Judul Konten']}*"
        f" dengan format ({tipe_str}) harus naik ke"
        f" {selected_row['Platform']} pada jam {selected_row['Jadwal Upload']}."
        f" Jangan lupa cek asetnya ya: {selected_row['Link Google Drive']}"
    )

    encoded_pesan = urllib.parse.quote(pesan_wa)
    whatsapp_url = (
        f"https://api.whatsapp.com/send?phone={nomor_tujuan}&text={encoded_pesan}"
    )

    st.markdown(
        f'<a href="{whatsapp_url}" target="_blank"><button'
        ' style="background-color:#25D366; color:white; padding:10px'
        ' 20px; border:none; border-radius:5px; cursor:pointer; font-size:16px;">📲'
        " Buka WhatsApp & Kirim Pesan</button></a>",
        unsafe_allow_html=True,
    )