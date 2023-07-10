from shiny import ui, module, reactive, render, Inputs, Outputs, Session, req
from shinywidgets import output_widget, render_widget


from utils.comp_analysis import (
    download_input,
    abc_summary_ui,
    abc_analysis_ui,
    numeric_summary_modal
)

from logic.func_num_summary import (
    numeric_summary_table,
    numeric_summary_plot
)

from logic.func_abc import (
    abc_analysis,
    summarise_abc,
    abc_plot
)


@module.ui
def mod_ui():
    
    return ui.TagList(
        abc_analysis_ui(),

        ui.br(), ui.br(),

        ui.output_ui(id="show_abc_summary")
    )


@module.server
def mod_server(
    input: Inputs, 
    output: Outputs, 
    session: Session, 
    var_data: dict,
    analysis_type_dict: dict
):
    
    # | numeric summary ----------------------------------------------------------
    @reactive.Effect
    @reactive.event(input.show_numeric_summary)
    def _():
        numeric_summary_modal()


    @output(id="numeric_summary_choice_output")
    @render.ui
    def numeric_summary_choice_output():

        if input.num_summary_choice() == "table":

            return ui.TagList(
                ui.div(
                    ui.output_data_frame(id="numeric_summary_data_frame"),

                    class_="modal-table"
                )
            )
        
        else:

            return ui.TagList(
                output_widget(id="numeric_summary_plot_widget", height="100%")
            )



    @output(id="numeric_summary_data_frame")
    @render.data_frame
    def numeric_summary_data_frame():

        req(input.show_numeric_summary)

        if input.num_summary_choice() == "table":

            num_data = numeric_summary_table(
                data=var_data["data"](),
                var_dict=var_data["var_dict"]()
            )

            if num_data["data"] is not None:

                return render.DataGrid(
                    num_data["data"],
                    row_selection_mode="none",
                    width="100%",
                    height="100%",
                )



    @output(id="num_summary_additions")
    @render.ui
    def num_summary_additions():

        req(input.show_numeric_summary)

        if input.num_summary_choice() != "table":

            return ui.TagList(
                ui.div(
                     ui.input_select(
                        id="var_selection",
                        label="variable",
                        choices={
                            "var_quantity": "Quantity",
                            "var_revenue": "Revenue"
                        },
                        selected="var_revenue",
                        width="150px"
                    ),

                    ui.input_numeric(
                        id="n_bins",
                        label="N. Bins",
                        value=30,
                        min=20, max=100, step=5,
                        width="100px"
                    ),

                    ui.input_switch(
                        id="log",
                        label="Log",
                        value=False
                    ),
                ),
            )



    @output(id="numeric_summary_plot_widget")
    @render_widget
    def numeric_summary_plot_widget():

        if input.num_summary_choice() != "table":
            return numeric_summary_plot(
                data=var_data["data"](),
                var_dict=var_data["var_dict"](),
                variable=input.var_selection(),
                output=input.num_summary_choice(),
                n_bins=input.n_bins(),
                log=input.log()
            )
            
            # @synchronize_size("numeric_summary_plot_widget")
            # def on_size_changed(width, height):
            #     widget.layout.width = width
            #     widget.layout.height = height

            # return widget


    # || ABC -------------------------------------------------------------------
    @reactive.Calc
    @reactive.event(input.run_abc_analysis)
    def abc_class_dict():

        req(input.a_percentege, input.b_percentege, input.c_percentege)

        return abc_analysis(
            data=var_data["data"](),
            var_dict=var_data["var_dict"](),
            scale=[input.a_percentege(), input.b_percentege(), input.c_percentege()]
        )
    

    @output(id="abc_raw_table")
    @render.data_frame
    def abc_raw_table():
        
        req(abc_class_dict)

        if abc_class_dict()["error"]:

            return None
        
        else:

            return render.DataGrid(
                abc_class_dict()["data"].head(10),
                row_selection_mode="none",
                width="100%",
                height="100%",
            )


    @output(id="show_abc_download")
    @render.ui
    def show_abc_download():

        req(abc_class_dict())

        if abc_class_dict()["error"]:

            return ui.TagList()
        
        else:

            return download_input("download_abc_raw")
        
    
    @session.download(filename="abc_classification.csv")
    def download_abc_raw():

        if abc_class_dict()["error"]:

            pass

        else:

            yield abc_class_dict()["data"].to_csv(index=False)

    
    # | summary |---------------------------------------------------------------
    @output(id="show_abc_summary")
    @render.ui
    def show_abc_summary():

        req(abc_class_dict())

        if abc_class_dict()["error"]:

            return ui.TagList()
        
        else:

            return abc_summary_ui()

    @reactive.Calc
    def abc_summary():

        req(abc_class_dict)

        if abc_class_dict()["error"]:

            return None
        
        else:

            return summarise_abc(
                data=abc_class_dict()["data"],
                var_dict=var_data["var_dict"](),
                clean_name=False
            )
        

    # table --------------------------
    @output(id="abc_table_summary_output")
    @render.data_frame
    def abc_table_summary_output():
        
        req(abc_class_dict())

        if input.show_abc_table_summary() % 2:
            if abc_class_dict()["error"]:

                return None
            
            else:

                af_data = summarise_abc(
                    data=abc_class_dict()["data"],
                    var_dict=var_data["var_dict"](),
                    clean_name=True
                )

            return render.DataGrid(
                af_data,
                row_selection_mode="none",
                width="100%",
                height="100%",
            )


    # plot ---------------------------
    @output(id="abc_product_ui")
    @render.ui
    def abc_product_ui():

        if input.show_abc_product_plot():

            return ui.TagList(
                output_widget(id="abc_product", height="100%"),
            )


    @output(id="abc_product")
    @render_widget
    @reactive.event(input.show_abc_product_plot)
    def abc_product():

        req(abc_summary)

        if input.show_abc_product_plot():

            return abc_plot(
                data=abc_summary(),
                plt_var="total_products"
            )
        

    # -------------------------------
    @output(id="abc_demand_ui")
    @render.ui
    def abc_demand_ui():

        if input.show_abc_demand_plot():

            return ui.TagList(
                output_widget(id="abc_demand", height="100%"),
            )


    @output(id="abc_demand")
    @render_widget
    @reactive.event(input.show_abc_demand_plot)
    def abc_demand():

        req(abc_summary)

        if input.show_abc_demand_plot():

            return abc_plot(
                data=abc_summary(),
                plt_var="total_demand"
            )

    # -----------------------------------

    @output(id="abc_revenue_ui")
    @render.ui
    def abc_revenue_ui():

        if input.show_abc_revenue_plot():

            return ui.TagList(
                output_widget(id="abc_revenue", height="100%"),
            )


    @output(id="abc_revenue")
    @render_widget
    @reactive.event(input.show_abc_revenue_plot)
    def abc_revenue():

        req(abc_summary)

        if input.show_abc_revenue_plot():

            return abc_plot(
                data=abc_summary(),
                plt_var="total_revenue"
            )

