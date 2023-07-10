from shiny import ui



def int_container(*args, add_class: str = '', **kwargs):

    return ui.div(
        class_=f"interactive-container {add_class}",
        *args,
        **kwargs
    )