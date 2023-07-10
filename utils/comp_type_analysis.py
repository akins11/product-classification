from shiny import ui
from faicons import icon_svg



def analysis_selection_ui(label: str, link_id: str):

    return ui.TagList(
        ui.div(
            ui.h4(label, class_="fw-bold text-decoration-underline"),
            

            ui.div(
                ui.input_action_link(
                    id=link_id,
                    label="",
                    icon=icon_svg(
                        "link", 
                        height="2em", 
                        margin_right="0"
                    )
                ),

                class_="analysis-selection-link"
            ),

            class_="analysis-link-container"
        )
    )