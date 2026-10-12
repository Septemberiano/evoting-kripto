import reflex as rx
from ..state import State

def admin_view() -> rx.Component:
    return rx.vstack(
        rx.heading("Dashboard Administrator E-Voting", size="7"),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Management User / DPT", value="tab_users"),
                rx.tabs.trigger("Management TPS", value="tab_tps"),
                rx.tabs.trigger("Brankas Suara & Dekripsi", value="tab_vault"),
                size="2",
            ),
            # --- TAB 1: MANAGEMENT USER ---
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Tambah Akun Pemilih (DPT)", size="4"),
                    rx.hstack(
                        rx.input(placeholder="Username Baru", on_change=State.set_new_username, value=State.new_username),
                        rx.input(placeholder="Password Baru", type="password", on_change=State.set_new_password, value=State.new_password),
                        rx.button("Tambah User", on_click=State.add_user, color_scheme="blue"),
                    ),
                    rx.heading("Daftar Pengguna Terdaftar", size="4", margin_top="15px"),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID"),
                                rx.table.column_header_cell("Username"),
                                rx.table.column_header_cell("Role"),
                                rx.table.column_header_cell("Aksi"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.user_list,
                                lambda u: rx.table.row(
                                    rx.table.cell(u["id"]),
                                    rx.table.cell(u["username"]),
                                    rx.table.cell(u["role"]),
                                    rx.table.cell(
                                        # PERBAIKAN: Kirim u["id"] langsung tanpa int()
                                        rx.button("Hapus", color_scheme="red", size="1", on_click=lambda: State.delete_user(u["id"]))
                                    ),
                                )
                            )
                        ),
                        width="100%",
                    ),
                    spacing="3",
                    padding_top="15px",
                ),
                value="tab_users",
            ),
            # --- TAB 2: MANAGEMENT TPS ---
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Tambah Data TPS / Wilayah", size="4"),
                    rx.hstack(
                        rx.input(placeholder="Kode TPS (misal: TPS-01)", on_change=State.set_new_kode_tps, value=State.new_kode_tps),
                        rx.input(placeholder="Nama Lokasi / Desa", on_change=State.set_new_nama_tps, value=State.new_nama_tps),
                        rx.button("Tambah TPS", on_click=State.add_tps, color_scheme="green"),
                    ),
                    rx.heading("Daftar TPS Terdaftar", size="4", margin_top="15px"),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID"),
                                rx.table.column_header_cell("Kode TPS"),
                                rx.table.column_header_cell("Nama Lokasi"),
                                rx.table.column_header_cell("Aksi"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.tps_list,
                                lambda t: rx.table.row(
                                    rx.table.cell(t["id"]),
                                    rx.table.cell(t["kode"]),
                                    rx.table.cell(t["nama"]),
                                    rx.table.cell(
                                        # PERBAIKAN: Kirim t["id"] langsung tanpa int()
                                        rx.button("Hapus", color_scheme="red", size="1", on_click=lambda: State.delete_tps(t["id"]))
                                    ),
                                )
                            )
                        ),
                        width="100%",
                    ),
                    spacing="3",
                    padding_top="15px",
                ),
                value="tab_tps",
            ),
            # --- TAB 3: BRANKAS SUARA ---
            rx.tabs.content(
                rx.vstack(
                    rx.hstack(
                        rx.button("Refresh Database Suara", on_click=State.load_db_votes, color_scheme="gray"),
                        rx.button("Buka Brankas & Dekripsi Suara", on_click=State.decrypt_all_votes, color_scheme="green"),
                    ),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID"),
                                rx.table.column_header_cell("TPS (Caesar Encrypted)"),
                                rx.table.column_header_cell("Suara (Super Encrypted)"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                State.raw_votes_db,
                                lambda v: rx.table.row(
                                    rx.table.cell(v["id"]),
                                    rx.table.cell(v["tps"]),
                                    rx.table.cell(v["pilihan"]),
                                )
                            )
                        ),
                        width="100%",
                    ),
                    rx.cond(
                        State.is_decrypted,
                        rx.vstack(
                            rx.divider(),
                            rx.heading("Hasil Perolehan Suara Terdekripsi", size="5", color="green"),
                            rx.foreach(
                                State.decrypted_results.entries(),
                                lambda item: rx.card(
                                    rx.hstack(
                                        rx.text(item[0], weight="bold"),
                                        rx.text(f"{item[1]} Suara", color="blue"),
                                        justify="between",
                                    )
                                )
                            ),
                            width="100%",
                        )
                    ),
                    spacing="3",
                    padding_top="15px",
                ),
                value="tab_vault",
            ),
            width="100%",
        ),
        width="100%",
        spacing="4",
    )