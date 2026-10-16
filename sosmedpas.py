from datetime import datetime, timedelta
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
          "Catatan",
      ]
  )

st.title("📱 Social Media Content Planner & Scheduler")
st.markdown(
    "Kelola jadwal postingan Instagram, simpan link aset Google Drive, dan"
    " pantau pengingat upload."
)

# Sidebar untuk Navigasi Menu
menu = st.sidebar.selectbox(
    "Pilih Menu",
    [
        "📋 Daftar Konten & Jadwal",
        "➕ Tambah Konten Baru",
        "⏰ Reminder & Notifikasi (H-2 Jam)",
    ],
)

# ==========================================
# MENU 1: DAFTAR KONTEN & JADWAL
# ==========================================
if menu == "📋 Daftar Konten & Jadwal":
  st.subheader("📋 Jadwal & Status Konten Sosial Media")

  df = st.session_state["content_db"]

  if df.empty:
    st.info(
        "Belum ada konten yang dijadwalkan. Silakan tambah melalui menu **Tambah"
        " Konten Baru**."
    )
  else:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
      filter_status = st.selectbox(
          "Filter Status", ["Semua", "Draft", "Scheduled", "Posted"]
      )
    with col_f2:
      filter_platform = st.selectbox(
          "Filter Platform", ["Semua", "Instagram", "TikTok", "YouTube", "Facebook"]
      )

    filtered_df = df.copy()
    if filter_status != "Semua":
      filtered_df = filtered_df[filtered_df["Status"] == filter_status]
    if filter_platform != "Semua":
      filtered_df = filtered_df[filtered_df["Platform"] == filter_platform]

    for index, row in filtered_df.iterrows():
      with st.container():
        st.markdown(f"### 📌 {row['Judul Konten']}")
        c1, c2, c3, c4 = st.columns(4)
        c1.write(f"**Platform:** {row['Platform']}")
        
        # Karena Tipe Konten sekarang berupa list (banyak), kita gabungkan jadi teks koma
        tipe_str = (
            ", ".join(row["Tipe Konten"])
            if isinstance(row["Tipe Konten"], list)
            else row["Tipe Konten"]
        )
        c2.write(f"**Tipe:** {tipe_str}")
        c3.write(f"**Jadwal:** {row['Jadwal Upload']}")
        c4.write(f"**Status:** {row['Status']}")

        if row["Link Google Drive"]:
          st.markdown(
              f"🔗 [Buka Aset di Google Drive]({row['Link Google Drive']})"
          )
        if row["Catatan"]:
          st.caption(f"Catatan: {row['Catatan']}")

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        if col_btn1.button("✅ Tandai Posted", key=f"post_{row['ID']}"):
          st.session_state["content_db"].loc[
              st.session_state["content_db"]["ID"] == row["ID"], "Status"
          ] = "Posted"
          st.rerun()
        if col_btn2.button("🗑️ Hapus", key=f"del_{row['ID']}"):
          st.session_state["content_db"] = st.session_state["content_db"][
              st.session_state["content_db"]["ID"] != row["ID"]
          ]
          st.rerun()
        st.divider()

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
      # DIUBAH MENJADI MULTISELECT (BISA PILIH LEBIH DARI SATU)
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
            "Tipe Konten": tipe_konten,  # Menyimpan list pilihan
            "Jadwal Upload": waktu_gabung.strftime("%Y-%m-%d %H:%M"),
            "Link Google Drive": link_gdrive,
            "Status": status,
            "Catatan": catatan,
        }

        st.session_state["content_db"] = pd.concat(
            [
                st.session_state["content_db"],
                pd.DataFrame([new_data]),
            ],
            ignore_index=True,
        )
        st.success("Berhasil! Konten baru berhasil ditambahkan ke jadwal.")
      else:
        st.warning(
            "Mohon isi Judul, Link Google Drive, dan minimal pilih satu Tipe"
            " Konten."
        )

# ==========================================
# MENU 3: REMINDER & NOTIFIKASI (H-2 JAM)
# ==========================================
elif menu == "⏰ Reminder & Notifikasi (H-2 Jam)":
  st.subheader("⏰ Pengecekan Reminder Upload (H-2 Jam)")
  st.markdown(
      "Fitur ini mendeteksi konten berstatus **Scheduled** yang jadwal uploadnya"
      " tinggal **2 jam lagi (atau sudah lewat tapi belum di-posting)**."
  )

  df = st.session_state["content_db"]

  if df.empty:
    st.info("Belum ada data konten.")
  else:
    scheduled_df = df[df["Status"] == "Scheduled"].copy()

    if scheduled_df.empty:
      st.success(
          "🎉 Aman! Tidak ada konten terjadwal yang mendesak saat ini."
      )
    else:
      waktu_sekarang = datetime.now()
      ada_alert = False

      for index, row in scheduled_df.iterrows():
        waktu_jadwal = datetime.strptime(row["Jadwal Upload"], "%Y-%m-%d %H:%M")
        selisih_waktu = waktu_jadwal - waktu_sekarang
        sisa_jam = selisih_waktu.total_seconds() / 3600

        if sisa_jam <= 2:
          ada_alert = True
          judul_k = (
              row["Judul Content"]
              if "Judul Content" in row
              else row["Judul Konten"]
          )
          tipe_str = (
              ", ".join(row["Tipe Konten"])
              if isinstance(row["Tipe Konten"], list)
              else row["Tipe Konten"]
          )

          st.error(
              f"🚨 **PERINGATAN UPLOAD DEKAT!** Konten **'{judul_k}'**"
              f" (Format: **{tipe_str}**) dijadwalkan tayang pada"
              f" **{row['Jadwal Upload']}**!"
          )
          st.write(
              f"🔗 [Akses File Google Drive Disini]({row['Link Google Drive']})"
          )

          nomor_tujuan = st.text_input(
              "Nomor WhatsApp Admin (awali 62):",
              value="6285793241231",
              key=f"wa_{row['ID']}",
          )
          pesan_wa = (
              f"Halo! Reminder nih, konten sosial media *{judul_k}*"
              f" dengan format ({tipe_str}) harus naik ke {row['Platform']}"
              f" pada jam {row['Jadwal Upload']}. Jangan lupa cek asetnya ya:"
              f" {row['Link Google Drive']}"
          )
          encoded_pesan = urllib.parse.quote(pesan_wa)
          whatsapp_url = (
              f"https://api.whatsapp.com/send?phone={nomor_tujuan}&text={encoded_pesan}"
          )

          st.markdown(
              f'<a href="{whatsapp_url}" target="_blank"><button'
              ' style="background-color:#25D366; color:white; padding:8px'
              ' 16px; border:none; border-radius:4px; cursor:pointer;">📲 Kirim'
              " Peringatan ke WhatsApp</button></a>",
              unsafe_allow_html=True,
          )
          st.divider()

      if not ada_alert:
        st.info(
            "Semua konten terjadwal masih berjarak lebih dari 2 jam dari waktu"
            " sekarang."
        )