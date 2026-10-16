from datetime import date, datetime
import sqlite3
import urllib.parse
import pandas as pd
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Social Media Planner & Scheduler", page_icon="📱", layout="wide"
)

# NAMA FILE DATABASE SQLITE
DB_NAME = "content_database.db"


# Fungsi untuk membuat koneksi dan tabel SQLite jika belum ada
def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_db (
            ID TEXT PRIMARY KEY,
            Judul_Konten TEXT,
            Platform TEXT,
            Tipe_Konten TEXT,
            Jadwal_Upload TEXT,
            Link_Google_Drive TEXT,
            Status TEXT,
            Approval TEXT,
            Catatan TEXT
        )
    """)
  conn.commit()
  conn.close()


# Inisialisasi Database SQLite
init_db()


# Fungsi untuk memuat data dari SQLite ke Pandas DataFrame
def load_database():
  conn = sqlite3.connect(DB_NAME)
  try:
    df = pd.read_sql("SELECT * FROM content_db", conn)
    if "Tipe_Konten" in df.columns:
      df["Tipe_Konten"] = df["Tipe_Konten"].apply(
          lambda x: x.split(", ") if isinstance(x, str) else []
      )
    df = df.rename(
        columns={
            "Judul_Konten": "Judul Konten",
            "Tipe_Konten": "Tipe Konten",
            "Jadwal_Upload": "Jadwal Upload",
            "Link_Google_Drive": "Link Google Drive",
        }
    )
  except Exception as e:
    df = pd.DataFrame(
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
  conn.close()
  return df


# Fungsi untuk menyimpan seluruh DataFrame ke SQLite
def save_database(df):
  conn = sqlite3.connect(DB_NAME)
  df_to_save = df.copy()
  df_to_save["Tipe Konten"] = df_to_save["Tipe Konten"].apply(
      lambda x: ", ".join(x) if isinstance(x, list) else str(x)
  )
  df_to_save = df_to_save.rename(
      columns={
          "Judul Konten": "Judul_Konten",
          "Tipe Konten": "Tipe_Konten",
          "Jadwal Upload": "Jadwal_Upload",
          "Link Google Drive": "Link_Google_Drive",
      }
  )
  df_to_save.to_sql("content_db", conn, if_exists="replace", index=False)
  conn.close()


# Inisialisasi Session State dengan Database SQLite
if "content_db" not in st.session_state:
  st.session_state["content_db"] = load_database()

if "Approval" not in st.session_state["content_db"].columns:
  st.session_state["content_db"]["Approval"] = "Pending Approval"
  save_database(st.session_state["content_db"])

st.title("📱 Social Media Content Planner & Scheduler")
st.markdown(
    "Kelola jadwal postingan, tabel berkotak rapi, filter tanggal, dan Approval"
    " Direksi (Menggunakan Database SQLite)."
)

# Sidebar untuk Navigasi Menu
st.sidebar.title("📌 Navigasi Menu")
menu = st.sidebar.radio(
    "Pilih Menu:",
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
if menu == "