from shiny import ui, module, reactive, render, Inputs, Outputs, Session, req
from shinywidgets import output_widget, render_widget


from utils.comp_analysis import (
    xyz_analysis_ui,
    download_input,
    numeric_summary_modal,
    trend_chart_modal,
    xyz_summary_ui
)

from logic.func_num_summary import (
    numeric_summary_table,
    numeric_summary_plot
)

from logic.func_xyz import (
    trend_plot,
    xyz_analysis,
    cv_summary_plot,
    xyz_summary,
    xyz_plot
)




@module.ui
def mod_ui():
    
    return ui.TagList(
        xyz_analysis_ui(),

        ui.br(), ui.br(),

        ui.output_ui(id="show_xyz_summary")
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


    # || XYZ --------------------------------------------------------------------
    @reactive.Calc
    @reactive.event(input.run_xyz_analysis)
    def xyz_class_dict():

        req(input.x_limit, input.y_limit)

        return xyz_analysis(
            data=var_data["data"](),
            var_dict=var_data["var_dict"](),
            scale=[input.x_limit(), input.y_limit()]
        )
    

    @output(id="xyz_raw_table")
    @render.data_frame
    def xyz_raw_table():

        req(xyz_class_dict)

        if xyz_class_dict()["error"]:

            return None
        
        else:

            return render.DataGrid(
                xyz_class_dict()["data"].round(3).head(10),
                row_selection_mode="none",
                width="100%",
                height="100%",
            )
    

    @output(id="show_xyz_download")
    @render.ui
    def show_xyz_download():

        req(xyz_class_dict())

        if xyz_class_dict()["error"]:

            return ui.TagList()
        
        else:

            return download_input("download_xyz_raw")
        

    @session.download(filename="xyz_classification.csv")
    def download_xyz_raw():

        if xyz_class_dict()["error"]:

            pass

        else:

            yield xyz_class_dict()["data"].to_csv(index=False)


    # | Summary ------------------------------------------------------------------
    @output(id="show_xyz_summary")
    @render.ui
    def show_xyz_summary():

        req(xyz_class_dict())

        if xyz_class_dict()["error"]:

            return ui.TagList()
        
        else:
    
            return xyz_summary_ui()


    @output(id="show_cv_summary_ui")
    @render.ui
    @reactive.event(input.show_cv_summary)
    def show_cv_summary_ui():

        if input.show_cv_summary():
            
            return ui.TagList(
                output_widget(id="cov_summary_plot")
            )
        
    
    @output(id="cov_summary_plot")
    @render_widget
    def cov_summary_plot():
        
        req(xyz_class_dict)

        if input.show_cv_summary():

            return cv_summary_plot(
                data=xyz_class_dict()["data"]
            )


    @output(id="xyz_summary_table_output")
    @render.data_frame
    @reactive.event(input.show_xyz_summary_table)
    def xyz_summary_table_output():

        req(xyz_class_dict)

        if input.show_xyz_summary_table():

            return render.DataGrid(
                    xyz_summary(xyz_class_dict()["data"], clean_names=True),
                    row_selection_mode="none",
                    width="100%",
                    height="100%",
                )
        

    @output(id="xyz_summary_plot_output")
    @render_widget
    @reactive.event(input.show_xyz_summary_plot)
    def xyz_summary_plot_output():

        req(xyz_class_dict)

        if input.show_xyz_summary_plot():

            return xyz_plot(data=xyz_class_dict()["data"])

