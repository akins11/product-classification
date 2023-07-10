from shiny import ui, module, reactive, render, Inputs, Outputs, Session, req
from shinywidgets import output_widget, render_widget


from utils.comp_analysis import (
    abc_xyz_analysis_ui,
    numeric_summary_modal,
    trend_chart_modal,
    download_input,
    abc_xyz_summary_ui
)

from logic.func_num_summary import (
    numeric_summary_table,
    numeric_summary_plot
)

from logic.func_xyz import trend_plot

from logic.func_abc_xyz import (
    abc_xyz_analysis,
    abc_xyz_summary_table,
    abc_xyz_plot
)



@module.ui
def mod_ui():

    return ui.TagList(
            abc_xyz_analysis_ui(),

            ui.br(), ui.br(),

            ui.output_ui(id="show_abc_xyz_summary")
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
        


    # | Trend chart summary ----------------------------------------------------
    @reactive.Effect
    @reactive.event(input.show_trend_chart)
    def _():

        trend_chart_modal()


    @output(id="trend_chart_output")
    @render_widget
    def trend_chart_output():

        req(input.trend_chart_variable(), input.trend_chart_agg_func())

        return trend_plot(
            data=var_data["data"](),
            var_dict=var_data["var_dict"](),
            plt_var=input.trend_chart_variable(),
            agg_fun=input.trend_chart_agg_func()
        )



    @reactive.Calc
    @reactive.event(input.run_ax_analysis)
    def abc_xyz_class_dict():
        req(
            input.ax_a_percentege, input.ax_b_percentege, input.ax_c_percentege,
            input.ax_x_limit, input.ax_y_limit
        )

        return abc_xyz_analysis(
            data=var_data["data"](),
            var_dict=var_data["var_dict"](),
            abc_scale=[input.ax_a_percentege(), input.ax_b_percentege(), input.ax_c_percentege()],
            xyz_scale=[input.ax_x_limit(), input.ax_x_limit()]
        )
    

    @output(id="ax_raw_table")
    @render.data_frame
    def ax_raw_table():

        req(abc_xyz_class_dict())

        if  abc_xyz_class_dict()["data"] is not None:

            return render.DataGrid(
                    abc_xyz_class_dict()["data"].round(3).head(15),
                    row_selection_mode="none",
                    width="100%",
                    height="100%",
                )
        

    @output(id="show_ax_download")
    @render.ui
    def show_ax_download():
        req(abc_xyz_class_dict())

        if abc_xyz_class_dict()["error"]:

            return ui.TagList()
        
        else:

            return download_input("download_ax_raw")
        

    @session.download(filename="abc-xyz_classification.csv")
    def download_ax_raw():

        if abc_xyz_class_dict()["error"]:

            pass

        else:

            yield abc_xyz_class_dict()["data"].to_csv(index=False)


    # | Summary -------------------------------------------------------
    @output(id="show_abc_xyz_summary")
    @render.ui
    def show_abc_xyz_summary():
        req(abc_xyz_class_dict())

        if abc_xyz_class_dict()["error"]:
            return ui.TagList()
        else:
            return abc_xyz_summary_ui()
        

    @output(id="abc_xyz_table_summary_output")
    @render.data_frame
    def abc_xyz_table_summary_output():

        req(abc_xyz_class_dict())

        if input.show_abc_xyz_summary_table():

            return render.DataGrid(
                    abc_xyz_summary_table(abc_xyz_class_dict()["data"], True),
                    row_selection_mode="none",
                    width="100%",
                    height="100%",
                )
        

    @reactive.Calc
    def ax_summary_data():

        req(abc_xyz_class_dict())

        if abc_xyz_class_dict()["data"] is not None:
            
            return abc_xyz_summary_table(abc_xyz_class_dict()["data"])
        
    
    # Product ---------------------------------------
    @output(id="ax_product_output")
    @render.ui
    def ax_product_output():

        if input.show_product():

            return ui.TagList(
                output_widget(id="ax_product_plot")
            )
        
    
    @output(id="ax_product_plot")
    @render_widget
    def ax_product_plot():

        req(ax_summary_data)

        if input.show_product():
            
            return abc_xyz_plot(
                data=ax_summary_data(),
                plt_var="total_sku"
            )
        

    # Demand -----------------------------------------
    @output(id="ax_demand_output")
    @render.ui
    def ax_demand_output():

        if input.show_demand():

            return ui.TagList(
                output_widget(id="ax_demand_plot")
            )
        
    
    @output(id="ax_demand_plot")
    @render_widget
    def ax_demand_plot():

        req(ax_summary_data)

        if input.show_demand():
            
            return abc_xyz_plot(
                data=ax_summary_data(),
                plt_var="total_demand"
            )
        
    # Revenue -------------------------------------------
    @output(id="ax_revenue_output")
    @render.ui
    def ax_revenue_output():

        if input.show_revenue():

            return ui.TagList(
                output_widget(id="ax_revenue_plot")
            )
        
    
    @output(id="ax_revenue_plot")
    @render_widget
    def ax_revenue_plot():

        req(ax_summary_data)

        if input.show_revenue():
            
            return abc_xyz_plot(
                data=ax_summary_data(),
                plt_var="total_revenue"
            )