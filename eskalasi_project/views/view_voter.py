import reflex as rx
from ..state import State

def voter_view() -> rx.Component:
    return rx.vstack(
        rx.heading("Bilik Suara Terenkripsi", size="6"),
        rx.cond(
            State.has_voted,
            rx.callout(
                "Anda telah memberikan suara. Terima kasih atas partisipasi Anda!",
                icon="check_check",
                color_scheme="green",
            ),
            rx.vstack(
                rx.text("Isi Data Pemilih (Data akan dienkripsi secara bertingkat):"),
                rx.input(placeholder="NIK Pemilih (AES-128)", on_change=State.set_nik_input, value=State.nik_input, width="100%"),
                rx.input(placeholder="Nama Lengkap (ChaCha20)", on_change=State.set_nama_input, value=State.nama_input, width="100%"),
                rx.input(placeholder="Kode TPS (Caesar Cipher)", on_change=State.set_tps_input, value=State.tps_input, width="100%"),
                rx.text("Pilih Pasangan Calon (Super Enkripsi 4 Layer):", weight="bold"),
                rx.radio(
                    State.kandidat_options,
                    value=State.pilihan_kandidat,
                    on_change=State.set_pilihan_kandidat,
                ),
                rx.button("Kirim Suara Terenkripsi", on_click=State.submit_vote, color_scheme="blue", size="3"),
                width="100%",
                spacing="3",
            ),
        ),
        rx.divider(),
        rx.heading("Visualizer Log Enkripsi (Menu 1 - 5)", size="4"),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(
                    State.encryption_logs,
                    lambda log: rx.code(log, color_scheme="gray", size="1")
                ),
                align="stretch",
            ),
            type="always",
            scrollbars="vertical",
            style={"height": "220px", "background": "#111", "padding": "10px", "border-radius": "8px"},
        ),
        width="100%",
        spacing="4",
    )