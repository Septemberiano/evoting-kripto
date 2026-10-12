import reflex as rx
from .state import State
from .views.view_login import login_view
from .views.view_voter import voter_view
from .views.view_admin import admin_view

def index() -> rx.Component:
    return rx.center(
        rx.cond(
            ~State.logged_in,
            login_view(),
            rx.container(
                rx.hstack(
                    rx.hstack(
                        rx.text(f"Pengguna: {State.username}", weight="bold"),
                        rx.badge(rx.cond(State.is_admin, "Administrator", "Pemilih (Voter)"), color_scheme=rx.cond(State.is_admin, "red", "green")),
                    ),
                    rx.button("Keluar (Logout)", on_click=State.logout, size="2", color_scheme="red"),
                    justify="between",
                    align="center",
                    width="100%",
                    margin_bottom="20px",
                ),
                # PERBAIKAN PENTING: Pengkondisian berdasarkan role admin
                rx.cond(
                    State.is_admin,
                    admin_view(),  # Jika Admin -> Tampilkan Dashboard Admin Lengkap
                    voter_view()   # Jika Voter -> Tampilkan Bilik Suara
                ),
                padding="20px",
                max_width="900px",
            )
        ),
        min_height="100vh",
        padding="20px",
    )

app = rx.App()
app.add_page(index)