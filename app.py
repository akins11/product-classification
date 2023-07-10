from shiny import App, Inputs, Outputs, Session, render, ui, reactive, req
from pathlib import Path
import shinyswatch
from pandas import read_csv, DataFrame
from faicons import icon_svg
import shiny.experimental as x


from logic.func_global import check_data

from module import (
    mod_selection, 
    mod_type_analysis,
    mod_analysis
)

from utils.comp_ui import int_container

app_ui = ui.page_fluid(
    shinyswatch.theme.yeti(),

    ui.tags.head(
        ui.tags.link(rel="stylesheet", href="style.css")
    ), 

    ui.div(
        ui.div(
            icon_svg(
                "truck-ramp-box", 
                fill="#000000", 
                margin_right="0",
                margin_left="0",
                height="2rem" 
            ),
  
            ui.h2("Product Classification", class_="text-start fw-bold"),

            class_="logo-title"
        ),

        ui.tags.a( 
            ui.tags.img(
                src="static/image/logo.svg",
                class_="logo-image"
            ),
            
            href="https://akins11.github.io/Porfolio/",
        ),

        class_="header-container"
    ),

    ui.br(), ui.br(),

    ui.div(
        icon_svg(
            "upload", 
            style="solid", 
            margin_left="0", 
            height="1.3rem", 
            fill="#888888"
        ),

        ui.h4("Data Upload", class_="fw-bold text-decoration-underline pt-1 st-text"),

        class_="section-title mt-4"
    ),
    
    x.ui.layout_column_wrap(
        1/3, 

        int_container(
            ui.input_file(
                id="uplaod_file", 
                label = "Upload .CSV:",
                accept=[".csv"], 
                multiple=False
            ),

            add_class="center"
        ),

        int_container(
            ui.output_ui(id="upload_n_row_ui"),

            add_class="center"
        ),

        int_container(
            ui.output_ui(id="upload_info", style="min-height: 6.1rem;"),

            add_class="center"
        )
    ),

    ui.br(),

    x.ui.layout_column_wrap(
        1,

       int_container(
            ui.output_data_frame(id="upload_table")
        )
    ),

    ui.br(),

    mod_selection.mod_ui("variable_selection_id"),

    mod_type_analysis.mod_ui("analysis_type_id"),

    mod_analysis.mod_ui("analysis_id"),

     ui.br(), ui.br(), ui.br()
)



def server(input: Inputs, output: Outputs, session: Session):

    @reactive.Calc
    @reactive.event(input.uplaod_file)
    def upload_data():
        upload_file_dict = input.uplaod_file()

        up_data = read_csv(upload_file_dict[0]["datapath"])
        
        up_data_dict = check_data(up_data)

        if up_data_dict["error"]:

            return up_data_dict["message"]
        
        else:

             return up_data_dict["data"]
        
    
    @output(id="upload_n_row_ui")
    @render.ui
    def upload_n_row_ui():

        req(upload_data)

        return ui.TagList(
            ui.div(
                ui.div(
                    icon_svg("list-ol", height="1em", margin_left="0", margin_right="0"),
                    ui.h5("Number of Row", class_="fw-light"),

                    class_="n-rows-header"
                ),

                ui.input_numeric(
                    id="upload_n_row",
                    label="",
                    value=5,
                    min=5, max=20, step=1
                ),

                class_="n-row-container"
            )
        )


    @output
    @render.ui
    def upload_info():

        req(upload_data)

        dim = upload_data().shape

        return ui.TagList(
            ui.div(
                icon_svg(
                    "circle-info", 
                    fill="#FFFFFF",
                    height="1.5em",
                    margin_left="0.1em", 
                    margin_right="0"
                ),

                ui.div(
                    ui.div(                    
                        ui.h6(
                            "Dataframe Summary", 
                            class_="fw-light fs-5 text-decoration-underline"
                        ),

                        class_="alert-header"
                    ),

                    ui.p(
                        "The Data Contain ",
                        ui.span(f"{dim[1]}", class_="fw-bold"),
                        " Columns & ",
                        ui.span(f"{dim[0]:,}", class_="fw-bold"),
                        " Rows.",
                        
                        ui.br(),

                        "Currently Showing ",
                        ui.span(input.upload_n_row(), class_="fw-bold"),
                        " Rows"

                    ),

                    class_="custom-alart__value"
                ),

                class_="custom-alart"
            )
        )


    @output
    @render.data_frame
    def upload_table():
        
        return render.DataGrid(
            upload_data().head(input.upload_n_row()),
            row_selection_mode="none",
            width="100%",
            height="100%",
        )
            
            
    var_data_dict = mod_selection.mod_server(
        "variable_selection_id", 
        upload_data
    )

    type_analysis_dict = mod_type_analysis.mod_server(
        "analysis_type_id",
        var_data_dict
    )

    mod_analysis.mod_server(
        "analysis_id",
        var_data_dict,
        type_analysis_dict
    )



www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)