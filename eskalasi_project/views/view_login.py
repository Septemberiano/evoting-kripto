import reflex as rx
from ..state import State

def login_view() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("E-Voting Kriptografi", size="7", align="center"),
            rx.text("Masuk ke Sistem Pemilihan Rahasia", color="gray"),
            rx.input(
                placeholder="Username",
                on_change=State.set_username,
                value=State.username,
                size="3",
                width="100%",
            ),
            rx.input(
                placeholder="Password",
                type="password",
                on_change=State.set_password,
                value=State.password,
                size="3",
                width="100%",
            ),
            rx.button("Masuk / Daftar", on_click=State.login, width="100%", size="3"),
            rx.cond(
                State.auth_message != "",
                rx.text(State.auth_message, color="red", size="2"),
            ),
            spacing="4",
            align="stretch",
        ),
        width="380px",
        padding="6",
    )