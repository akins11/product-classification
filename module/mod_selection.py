from shiny import ui, module, reactive, render, Inputs, Outputs, Session, req
from pandas import DataFrame
from faicons import icon_svg
import shiny.experimental as x


from logic.func_global import (
    clean_date_variable, 
    date_summary,
    check_selected_variables,
    organize_data,
    extract_duplicate_variable
)

from utils.comp_selection import (
    selection_container,
    variable_info_output,
    sku_message_ui,
    sku_variable_selection_output,
    date_variable_selection_output,
    error_header,
    warning_header,
    quantity_variable_selection_output,
    revenue_variable_selection_output
)



@module.ui
def mod_ui():

    return ui.TagList(
        ui.div(
            icon_svg(
                "pen-to-square", 
                style="solid", 
                margin_left="0", 
                height="1.3rem", 
                fill="#888888"
            ),

            ui.h4("Variable Selection", class_="fw-bold text-decoration-underline pt-1"),

            class_="section-title mt-4"
        ),

        x.ui.layout_column_wrap(
            1/4,

            selection_container(
                "Product (SKU)", 
                "sku_info_btn", 
                "sku_info_output",
                "selected_sku", 
                "sku_select_output"
            ),

            selection_container(
                "Date", 
                "date_info_btn",
                "date_info_output", 
                "selected_date", 
                "date_select_output"
            ),

            selection_container(
                "Quantity", 
                "quantity_info_btn",
                "quantity_info_output",  
                "selected_quantity", 
                "quantity_select_output"
            ),

            selection_container(
                "Revenue", 
                "revenue_info_btn",
                "revenue_info_output",  
                "selected_revenue", 
                "revenue_select_output"
            ),

        ),

        ui.br(),

        ui.div(
            ui.input_action_button(
                id="finished_selection", 
                label="Done",
                icon=icon_svg("file-export"),
                class_="btn-dark btn-lg"
            ),

            class_="finish-selection-container"
        ),

        ui.br(),

        x.ui.layout_column_wrap(
            1/2,

            ui.output_ui("all_selection_error_message"),

            ui.output_ui("data_parsing_error_message")
        )
    )






@module.server
def mod_server(
    input: Inputs, 
    output: Outputs, 
    session: Session, 
    upload_data: DataFrame
):
    
    @reactive.Effect
    def _():
        
        req(upload_data)

        cols = upload_data().columns.tolist()

        cols_dict = {c: c for c in cols} 
        cols_dict["no_selection"] = "No selection yet"

        ui.update_select(
            id="selected_sku",
            choices=cols_dict,
            selected="no_selection",
            session=session
        )

        ui.update_select(
            id="selected_date",
            choices=cols_dict,
            selected="no_selection",
            session=session
        )

        ui.update_select(
            id="selected_quantity",
            choices=cols_dict,
            selected="no_selection",
            session=session
        )

        ui.update_select(
            id="selected_revenue",
            choices=cols_dict,
            selected="no_selection",
            session=session
        )



    # Variable dictionary ------------------------------------------------------------
    @reactive.Calc
    def var_dict():

        return {
            "var_sku": input.selected_sku(),
            "var_date": input.selected_date(),
            "var_quantity": input.selected_quantity(),
            "var_revenue": input.selected_revenue()
        }

    
    # | SKU --------------------------------------------------------------------------
    @output(id="sku_info_output")
    @render.ui
    def sku_info_output():

        if input.sku_info_btn() % 2:
            
            return variable_info_output("var_sku")


    @reactive.Calc
    @reactive.event(input.selected_sku)
    def sku_select_output_dict():

        req(var_dict())

        return sku_variable_selection_output(upload_data(), var_dict())
    
    @output(id="sku_select_output")
    @render.ui
    def sku_select_output():

        req(sku_select_output_dict())

        return sku_message_ui(sku_select_output_dict())


     
    # | Date ------------------------------------------------------------------------
    @output(id="date_info_output")
    @render.ui
    def date_info_output():

        if input.date_info_btn() % 2:

            return variable_info_output("var_date")
        

    @output(id="date_select_output")
    @render.ui
    def date_select_output():

        req(var_dict())

        return date_variable_selection_output(upload_data(), var_dict())
    

    @reactive.Calc
    def clean_date_data_dict():

        req( var_dict())

        if var_dict()["var_date"] not in ["no_selection", "no_variable"]:

            return clean_date_variable(upload_data(), var_dict())
        
        else:

            return {"data": upload_data(), "error": False, "message": None}
        

    @reactive.Effect
    @reactive.event(input.date_summary_modal_btn)
    def _():

        return ui.modal_show(
            ui.modal(
                ui.div(
                    ui.input_radio_buttons(
                        id="date_summary_query", 
                        label="Filter By",
                        choices={
                            "all": "All available year", 
                            "twelve": "With all 12 months",
                            "six_above": "With 6 months & above"
                        }
                    ),

                    ui.br(),

                    ui.output_ui(id="date_summary_table_error"),

                    ui.div(
                        ui.output_data_frame(id="date_summary_table"),

                        class_="modal-table"
                    ),
                ),
                title="Date Summary",
                size="m",
                easy_close=True
            )
        )
    

    @reactive.Calc
    def date_summary_dict():

        req(clean_date_data_dict())

        if clean_date_data_dict()["error"]:

            return {"data": None, "error": True, "message": clean_date_data_dict()["message"]}
        
        else:

            return date_summary(
                clean_date_data_dict()["data"], 
                var_dict(), 
                input.date_summary_query()
            )


    @output(id="date_summary_table")
    @render.data_frame
    def date_summary_table():

        req(date_summary_dict())

        if date_summary_dict()["error"]:

            return render.DataGrid(
                DataFrame()
            )
        
        else:

            return render.DataGrid(
                date_summary_dict()["data"],
                row_selection_mode="multiple",
                width="100%",
                height="100%",
            )
        


    @output(id="date_summary_table_error")
    @render.ui
    def date_summary_table_error():

        if date_summary_dict()["error"]:

            return ui.TagList(
                ui.div(
                    error_header(),

                    ui.hr(),

                    ui.p(
                        """
                        Date Summary returned an empty table because date summary failed. 
                        """,
                        ui.br(),
                        # date_summary_dict()["message"],
                        """
                        Please Check the selected date variable. 
                        """
                    ),

                    class_="alert alert-danger"
                )
            )



    # | Quantity -------------------------------------------------------------------
    @output(id="quantity_info_output")
    @render.ui
    def quantity_info_output():

        if input.quantity_info_btn() % 2:

            return variable_info_output("var_quantity")
        

    @output(id="quantity_select_output")
    @render.ui
    @reactive.event(input.selected_quantity)
    def quantity_select_output():

        return quantity_variable_selection_output(
            data=upload_data(),
            var_dict=var_dict()
        )



    # | Revenue --------------------------------------------------------------------
    @output(id="revenue_info_output")
    @render.ui
    def revenue_info_output():

        if input.revenue_info_btn() % 2:

            return variable_info_output("var_revenue")



    @output
    @render.ui
    @reactive.event(input.selected_revenue)
    def revenue_select_output():

        return revenue_variable_selection_output(
                data=upload_data(),
                var_dict=var_dict()
            )



    # | Clean Data ----------------------------------------------------------------
    @reactive.Calc
    def all_selected_variables():

        return check_selected_variables(var_dict())
    

    @reactive.Calc
    @reactive.event(input.finished_selection)
    def clean_uploaded_data():

        if clean_date_data_dict()["error"] or len(set(var_dict().values())) != 4:

            return {"data": None, "is_empty": True}
        
        else:

            if all_selected_variables()["is_all_selected"]:

                clean_dict = organize_data(
                    data=clean_date_data_dict()["data"], 
                    var_dict=var_dict(), 
                    year=int(input.selected_year()),
                    drop_zero_qty=input.remove_zero_quantity()
                )

                if clean_dict["error"]:

                    return {"data": None, "is_empty": True}
                
                else:

                    return {"data": clean_dict["data"], "is_empty": False}
                
            else:

                return {"data": None, "is_empty": True}
            
        
    # | Error Message ----------------------------------------------------------
    @output(id="all_selection_error_message")
    @render.ui
    @reactive.event(input.finished_selection)
    def all_selection_error_message():

        if all_selected_variables()["is_all_selected"] == False and input.finished_selection() > 0:
        
            length = len(all_selected_variables()["non_selected_vars"])

            var_len = "inputs" if length > 1 else "input"

            variable_tags = ui.TagList()

            for var in all_selected_variables()["non_selected_vars"]:

                variable_tags.append(
                    ui.div(var, class_="badge bg-dark border text-light m-2 w-25")
                )

            return ui.TagList(
                ui.div(
                    warning_header(),

                    ui.hr(),

                    ui.p(
                        """
                        To proceed, all variable inputs must be chosen. This is to clearly
                        indicate that all requested variables are required. 
                        """,
                        class_="fs-5"
                    ),

                    ui.p(
                        f"The following {var_len} currently hold no selected variable :",
                        ui.br(),
                        variable_tags
                    ),

                    class_="alert alert-warning selection-msg-box"
                )
            )



    @output(id="data_parsing_error_message")
    @render.ui
    @reactive.event(input.finished_selection)
    def data_parsing_error_message():

        req(clean_uploaded_data())

        if len(set(var_dict().values())) != 4:

            duplicate_selection = extract_duplicate_variable(var_dict())

            var_label = "variables" if len(duplicate_selection) > 1 else "variable"

            variable_tags = ui.TagList()

            for var in duplicate_selection:

                variable_tags.append(
                    ui.div(var, class_="badge bg-dark border text-light m-2 w-25")
                )

            return ui.TagList(
                ui.div(
                    error_header(),

                    ui.hr(),

                    ui.p(
                        ui.span("Invalid selection of variables.", class_="fw-bold"),
                        """ 
                        Please ensure that all requested variables represent one of the 
                        following: SKU, Date, Quantity, or Revenue.
                        """
                    ),

                    ui.p(
                        f"The following {var_label} have been selected more than once:",

                        ui.br(),

                        variable_tags
                    ),


                    class_="alert alert-danger selection-msg-box"
                )
            )

        if clean_uploaded_data()["is_empty"] and all_selected_variables()["is_all_selected"]:

            return ui.TagList(
                ui.div(
                    error_header(),

                    ui.hr(),

                    ui.p(
                        """
                        An error has occurred during the parsing of selected variables to the 
                        approperate data types required for the analysis. Please ensure that all variables
                        have the correct attributes corresponding to their respective input titles.
                        """
                    ),

                    class_="alert alert-danger selection-msg-box"
                )
            )
        


    # | Output --------------------------------------------------------------------------
    @reactive.Calc
    def is_empty_data():

        return clean_uploaded_data()["is_empty"]
    

    @reactive.Calc
    def final_data():

        return clean_uploaded_data()["data"]
    


    return {"is_empty": is_empty_data, "var_dict": var_dict, "data": final_data}