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
    "Kelola jadwal postingan, tabel berkotak rapi, filter tanggal, dan Approval"
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
          "💡 **Cara Kelola:** Ubah kolom **Status** langsung di tabel, atau"
          " gunakan tombol **✏️ Edit** untuk mengubah detail, dan tombol **🗑️"
          " Hapus** untuk menghapus baris."
      )

      edit_df = filtered_df.copy()
      edit_df["Tipe Konten"] = edit_df["Tipe Konten"].apply(
          lambda x: ", ".join(x) if isinstance(x, list) else x
      )

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
                  "Catatan",
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
          },
          disabled=[
              "Judul Konten",
              "Platform",
              "Tipe Konten",
              "Jadwal Upload",
              "Approval",
              "Link Google Drive",
              "Catatan",
          ],
          use_container_width=True,
          hide_index=True,
          key="manager_table_editor",
      )

      if st.button("💾 Simpan Perubahan Status", type="primary"):
        for index, row in edited_df.iterrows():
          row_id = row["ID"]
          new_status = row["Status"]
          st.session_state["content_db"].loc[
              st.session_state["content_db"]["ID"] == row_id, "Status"
          ] = new_status

        st.success("Perubahan status berhasil disimpan!")
        st.rerun()

      st.markdown("---")
      st.subheader("⚙️ Aksi Cepat (Edit & Hapus per Baris)")

      for index, row in filtered_df.iterrows():
        c_act1, c_act2, c_act3 = st.columns([3, 1, 1])
        with c_act1:
          st.write(
              f"📌 **{row['Judul Konten']}** ({row['Platform']} -"
              f" {row['Jadwal Upload']})"
          )
        with c_act2:
          if st.button("✏️ Edit", key=f"edit_btn_{row['ID']}"):
            st.session_state["edit_id"] = row["ID"]
            st.rerun()
        with c_act3:
          if st.button("🗑️ Hapus", key=f"del_btn_{row['ID']}"):
            st.session_state["content_db"] = st.session_state["content_db"][
                st.session_state["content_db"]["ID"] != row["ID"]
            ]
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
            edit_judul = st.text_input("Judul / Tema Konten", value=r_data["Judul Konten"])
            
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
                  else [r_data["Tipe Konten"]]
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
                parsed_dt = datetime.strptime(r_data["Jadwal Upload"], "%Y-%m-%d %H:%M")
                def_date = parsed_dt.date()
                def_time = parsed_dt.time()
              except:
                def_date = date.today()
                def_time = datetime.now().time()

              edit_tanggal = st.date_input("Tanggal Upload", value=def_date)
              edit_jam = st.time_input("Jam Upload", value=def_time)

            edit_gdrive = st.text_input(
                "Link Google Drive", value=r_data["Link Google Drive"]
            )
            
            status_list = ["Draft", "Scheduled", "Posted"]
            s_idx = (
                status_list.index(r_data["Status"])
                if r_data["Status"] in status_list
                else 0
            )
            edit_status = st.selectbox("Status", status_list, index=s_idx)
            
            edit_catatan = st.text_area("Catatan Tambahan / Copywriting", value=r_data["Catatan"])

            col_submit_e1, col_submit_e2 = st.columns(2)
            with col_submit_e1:
              btn_update = st.form_submit_button("💾 Update Perubahan", type="primary")
            with col_submit_e2:
              btn_cancel = st.form_submit_button("❌ Batal")

            if btn_update:
              gabung_waktu = datetime.combine(edit_tanggal, edit_jam)
              st.session_state["content_db"].loc[
                  st.session_state["content_db"]["ID"] == target_id,
                  [
                      "Judul Konten",
                      "Platform",
                      "Tipe Konten",
                      "Jadwal Upload",
                      "Link Google Drive",
                      "Status",
                      "Catatan",
                  ],
              ] = [
                  edit_judul,
                  edit_platform,
                  edit_tipe,
                  gabung_waktu.strftime("%Y-%m-%d %H:%M"),
                  edit_gdrive,
                  edit_status,
                  edit_catatan,
              ]
              del st.session_state["edit_id"]
              st.success("Perubahan konten berhasil disimpan!")
              st.rerun()

            if btn_cancel:
              del st.session_state["edit_id"]
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
      "Direksi dapat memeriksa materi konten, mengecek aset Google Drive,"
      " catatan, dan memberikan persetujuan dengan **sekali klik**."
  )

  df = st.session_state["content_db"]

  if df.empty:
    st.info("Belum ada konten yang diajukan.")
  else:
    pending_df = df[df["Approval"] == "Pending Approval"].copy()

    pilih_tgl_app = st.date_input(
        "📅 Filter Tanggal Pengajuan", value=None, key="filter_tgl_app"
    )
    if pilih_tgl_app:
      tgl_str = pilih_tgl_app.strftime("%Y-%m-%d")
      pending_df = pending_df[
          pending_df["Jadwal Upload"].str.startswith(tgl_str)
      ]

    st.markdown("### ⏳ Konten Menunggu Persetujuan")
    if pending_df.empty:
      st.success(
          "🎉 Tidak ada konten yang menunggu approval untuk tanggal tersebut."
      )
    else:
      for index, row in pending_df.iterrows():
        tipe_str = (
            ", ".join(row["Tipe Konten"])
            if isinstance(row["Tipe Konten"], list)
            else row["Tipe Konten"]
        )

        with st.container(border=True):
          c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.2, 1.2, 1.4])

          with c1:
            st.markdown(f"📌 **{row['Judul Konten']}**")
            st.caption(
                f"Platform: {row['Platform']} | Tipe: {tipe_str}"
            )

          with c2:
            st.markdown("🕒 **Jadwal:**")
            st.write(row["Jadwal Upload"])

          with c3:
            st.markdown("📂 **GDrive:**")
            if row["Link Google Drive"]:
              st.markdown(f"[Buka Link]({row['Link Google Drive']})")
            else:
              st.write("-")

          with c4:
            st.markdown("📝 **Catatan:**")
            st.write(row["Catatan"] if row["Catatan"] else "-")

          with c5:
            st.markdown("⚡ **Approval:**")
            btn_app, btn_rej = st.columns(2)
            with btn_app:
              if st.button(
                  "✅", key=f"app_{row['ID']}", help="Setujui (Approve)"
              ):
                st.session_state["content_db"].loc[
                    st.session_state["content_db"]["ID"] == row["ID"],
                    "Approval",
                ] = "Approved"
                st.success("Disetujui!")
                st.rerun()
            with btn_rej:
              if st.button("❌", key=f"rej_{row['ID']}", help="Tolak (Reject)"):
                st.session_state["content_db"].loc[
                    st.session_state["content_db"]["ID"] == row["ID"],
                    "Approval",
                ] = "Rejected"
                st.warning("Ditolak.")
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

      pilih_tgl_hist = st.date_input(
          "📅 Filter Tanggal Riwayat", value=None, key="filter_tgl_hist"
      )
      hist_df = df.copy()
      if pilih_tgl_hist:
        tgl_hist_str = pilih_tgl_hist.strftime("%Y-%m-%d")
        hist_df = hist_df[
            hist_df["Jadwal Upload"].str.startswith(tgl_hist_str)
        ]

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
                  "Jadwal Upload",
                  "Catatan",
              ]
          ],
          use_container_width=True,
          hide_index=True,
      )

# ==========================================
# MENU 5: KIRIM WHATSAPP REMINDER
# ==========================================
elif menu == "⏰ Kirim WhatsApp Reminder":
  st.subheader("📲 Kirim Peringatan Cepat ke WhatsApp Tim")
  st.markdown(
      "Pilih konten yang mau diingatkan, lalu pilih nama / nomor WhatsApp anggota"
      " tim tujuan."
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
        "Reza": "6281321686233",
        "Emma": "628175731188",
        "Gilang": "6281809830066",
        "Surya": "6281945678904",
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
        else selected_row["Tipe Konten"]
    )
    pesan_wa = (
        "Halo! Reminder nih, konten sosial media *"
        + str(selected_row["Judul Konten"])
        + "* dengan format ("
        + str(tipe_str)
        + ") harus naik ke "
        + str(selected_row["Platform"])
        + " pada jam "
        + str(selected_row["Jadwal Upload"])
        + ". Jangan lupa cek asetnya ya: "
        + str(selected_row["Link Google Drive"])
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