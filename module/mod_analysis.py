from shiny import ui, module, reactive, render, Inputs, Outputs, Session, req, session
from shinywidgets import output_widget, register_widget, render_widget


from utils.comp_analysis import (
    numeric_summary_modal,
    trend_chart_modal
)

from logic.func_num_summary import (
    numeric_summary_table,
    numeric_summary_plot
)


from module import (
    mod_abc,
    mod_xyz,
    mod_abc_xyz
)


@module.ui
def mod_ui():

    return ui.TagList(

        ui.output_ui("analysis_ui")
    )



@module.server
def mod_server(
    input: Inputs, 
    output: Outputs, 
    session: Session, 
    var_data: dict,
    analysis_type_dict: dict
):
    
    @reactive.Calc
    def selected_value():
        if analysis_type_dict["is_selected"]():

            return True
        
        else:

            return False
    

    @output(id="analysis_ui")
    @render.ui
    def analysis_ui():

        if analysis_type_dict["is_selected"]():

            return ui.TagList(
                ui.panel_main(
                    ui.navset_hidden(
                        ui.nav(
                            None, 
                            
                            mod_abc.mod_ui("abc_module_id"),

                            value="abc_analysis"
                        ),

                        ui.nav(
                            None, 
                            mod_xyz.mod_ui("xyz_module_id"),
                            value="xyz_analysis"
                        ),

                        ui.nav(
                            None, 
                            mod_abc_xyz.mod_ui("abc_xyz_module_id"), 
                            value="abc_xyz_analysis"
                        ),

                        id="hidden_tabs",
                        selected="abc_analysis"
                    )
                )
            )

        else:

            return ui.TagList()
        

    @reactive.Effect
    @reactive.event(selected_value)
    def _():
        ui.update_navs("hidden_tabs", selected=analysis_type_dict["value"]())


    # || ABC -------------------------------------------------------------------
    mod_abc.mod_server(
        "abc_module_id",
        var_data,
        analysis_type_dict
    )

    # || XYZ --------------------------------------------------------------------
    mod_xyz.mod_server(
        "xyz_module_id",
        var_data,
        analysis_type_dict
    )

    # || ABC-XYZ ----------------------------------------------------------------
    mod_abc_xyz.mod_server(
        "abc_xyz_module_id",
        var_data,
        analysis_type_dict
    )

















def synchronize_size(output_id):
    def wrapper(func):
        input = session.get_current_session().input

        @reactive.Effect
        def size_updater():
            func(
                input[f".clientdata_output_{output_id}_width"](),
                input[f".clientdata_output_{output_id}_height"](),
            )

        # When the output that we're synchronizing to is invalidated,
        # clean up the size_updater Effect.
        reactive.get_current_context().on_invalidate(size_updater.destroy)

        return size_updater

    return wrapper