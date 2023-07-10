from shiny import ui, module, reactive, render, Inputs, Outputs, Session, req
import shiny.experimental as x

from utils.comp_type_analysis import analysis_selection_ui


@module.ui
def mod_ui():

    return ui.TagList(
        ui.output_ui(id="show_analysis_selection_ui")
    )



@module.server
def mod_server(
    input: Inputs, 
    output: Outputs, 
    session: Session, 
    var_data_dict: dict
):
    
    @output(id="show_analysis_selection_ui")
    @render.ui
    def show_analysis_selection_ui():

        if var_data_dict["is_empty"]():

            return ui.TagList()
        
        else:

            return ui.TagList(
                x.ui.layout_column_wrap(
                    1/3,

                    analysis_selection_ui("ABC Analysis", "selected_abc"),

                    analysis_selection_ui("XYZ Analysis", "selected_xyz"),

                    analysis_selection_ui("ABC-XYZ Analysis", "selected_abc_xyz"),
                )
            )
        

    analysis_type = reactive.Value("no_selection")

    @reactive.Effect
    @reactive.event(input.selected_abc)
    def _():

        if input.selected_abc():

            analysis_type.set("abc_analysis")


    @reactive.Effect
    @reactive.event(input.selected_xyz)
    def _():

        if input.selected_xyz():

            analysis_type.set("xyz_analysis")


    @reactive.Effect
    @reactive.event(input.selected_abc_xyz)
    def _():

        if input.selected_abc_xyz():

            analysis_type.set("abc_xyz_analysis")   

    
    @reactive.Calc
    def is_selected_analysis():

        if analysis_type.get() == "no_selection":

            return False
        
        else:

            return True
        
    return {"is_selected": is_selected_analysis, "value": analysis_type}