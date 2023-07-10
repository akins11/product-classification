from shiny import ui, session
from pandas import to_datetime, DataFrame
from faicons import icon_svg

from utils.info_text import variable_info

from logic.func_global import (
    clean_date_variable,
    detect_multiple_years,
    recommended_year,
    check_quantity,
    check_revenue
)

empty_select_input = {"no_variable": "Empty variable"}


def selection_container(
        box_label: str,
        info_id: str,
        info_output_id: str,
        select_id: str,
        output_ui_id: str
):
    
    return ui.TagList(
        ui.div(
            ui.div(
                ui.tags.h5(box_label, class_="fw-bold"),

                ui.input_action_link(
                    id=info_id, 
                    label="", 
                    icon=icon_svg("caret-down", height="1.8rem", fill="#5E5E5E")
                ),
                
                class_="selection-box-header"
            ),

            ui.output_ui(id=info_output_id),

            ui.input_select(
                id=select_id, 
                label="",
                choices=empty_select_input
            ),
        
            ui.output_ui(id=output_ui_id),
            
            class_="selection-box py-2 mx-1 my-2"
        )
    )


def variable_info_output(variable):

    return ui.TagList(
            ui.br(),

            ui.div(
                icon_svg("circle-info", height="1.3rem"),

                ui.br(),

                ui.p(variable_info[variable]),

                style="transition: all .5s ease;",
                class_="alert alert-info text-light fw-bold"
            )
        )



def error_header():
    return ui.div(
        icon_svg("rectangle-xmark", margin_left="0", height="1.8rem"),

        ui.h4("Error!!", class_="alert-heading pt-1"),

        class_="alert-header"
    )

def success_header(label: str):
    return ui.div(
        icon_svg("circle-check", margin_left="0", height="1.7rem"),
        
        ui.h4(label, class_="alert-heading pt-1"),

        class_="alert-header"
    )

def warning_header():
    return ui.div(
        icon_svg("triangle-exclamation", margin_left="0", height="1.5rem"),
        
        ui.h4("Warning!!", class_="alert-heading pt-1"),

        class_="alert-header"
    )


# SKU ------------------------------------------
def sku_message_ui(output_dict: dict):

    if output_dict["error"]:

        return ui.TagList(
            ui.div(
                error_header(),

                ui.hr(),

                ui.p(
                    "The data can not processed as ",
                    ui.span("Only a Single Unique Product SKU has been Detected.", class_="fw-bolder"),
                    " To proceed with the analysis, ",
                    ui.span(
                        "There must be multiple product SKU present in the data",
                        class_="fw-bold"
                    )
                ),

                class_="alert alert-danger"
            )
        )
    
    else:

        if output_dict["selection"]:

            return ui.TagList(
                ui.div(
                    success_header("SKU"),

                    ui.hr(),
                    
                    ui.p(
                        "There are a total of ",
                        ui.span(f"{output_dict['number_sku']:,}", class_="fw-bold fs-5"),
                        " distinct product SKU present in the data"
                    ),

                    class_="alert alert-success"
                )
            )
        
        else:

            return ui.TagList(ui.div())
        

def sku_variable_selection_output(data: DataFrame, var_dict: dict) -> dict:

    if var_dict["var_sku"] not in ["no_selection", "no_variable"]:

        number_unique_sku = data[var_dict["var_sku"]].nunique()

        if number_unique_sku > 1:
            return {"error": False, "number_sku": number_unique_sku, "selection": True}
        else:
            return {"error": True, "number_sku": number_unique_sku, "selection": True}
    else:
        return {"error": False, "number_sku": 0, "selection": False}
    

# Date -----------------------------------------
def date_message_ui(type: str, year: int = None, date_var: str = None):

    if type == "error_div":

        return ui.TagList(
            ui.div(
                error_header(),

                ui.hr(),

                ui.p(
                    "An issue has arisen during the conversion of ",
                    ui.span(date_var, class_="fw-bold"),
                    " to a date (Data-type).",
                    ui.br(),
                    "Please verify the selected date variable for any errors."
                ),

                class_="alert alert-danger"
            )
        )
    
    else:

        return ui.TagList(
            ui.div(
                success_header("Date"),

                ui.hr(),

                ui.p(
                    "The data indicate the presence of only one year ",
                    ui.span(f"{year}.", class_="fw-bold"),
                    ui.br(),
                    "Therefore, ",
                    ui.span(year, class_="fw-bold"),
                    " will be utilized as the analysis year.",
                    ui.br(),
                    ui.span("[", class_="fw-bolder"), ui.br(),
                    f"""
                    It is important to double-check the selected date variable if ({year})
                    does not correspond to a year in the  data.
                    """,
                    ui.br(),
                    ui.span("]", class_="fw-bolder"),
                ),

                class_="alert alert-info"
            )
        )
    

def date_year_selection(available_year: list, selected_year: int = None):

    available_choice = {yr: yr for yr in available_year}

    return ui.TagList(
        ui.div(
            ui.input_select(
                id="selected_year",
                label="Select Year",
                choices=available_choice,
                selected=selected_year,
                width="100px"
            ),

            ui.div(
                ui.input_action_link(
                    id="date_summary_modal_btn", 
                    label="",
                    icon=icon_svg(
                        "calendar-days", 
                        fill="#0B132B", 
                        height="1.7em",
                        margin_right="0"
                    )
                ),

                class_="year-selection-modal-btn"
            ),

            class_="year-selection"
        ),

        ui.div(
            success_header("Date"),

            class_="alert alert-success mt-1"
        )
    )


def date_variable_selection_output(data: DataFrame, var_dict: dict):

    if var_dict["var_date"] not in ["no_selection", "no_variable"]:

        date_var = var_dict["var_date"]

        data_dict = clean_date_variable(data, var_dict)

        if data_dict["error"]:

            return date_message_ui(type="error_div", date_var=date_var)
        
        else:

            data = data_dict["data"]

            multi_years = detect_multiple_years(data, var_dict)

            if multi_years["is_multiple"]:

                recommend_dict = recommended_year(data, var_dict)

                if recommend_dict["error"]:

                    return date_year_selection(multi_years["unique"])
                
                else:

                    return date_year_selection(multi_years["unique"], int(recommend_dict["value"]))
                
            else:

                return date_message_ui("info_div", multi_years["unique"])
            


# Quantity --------------------------------------
def filter_out_zero_quantity_checkbox():

    return ui.TagList(
        ui.input_checkbox(
            id="remove_zero_quantity",
            label="Filter out zero quantities",
            value=False
        )
    )


def quantity_select_output(check_dict: dict, quantity_var: str = None):

    if check_dict["error"]:

        if "numeric" in check_dict["message"]: 

            return ui.TagList(
                ui.div(
                    error_header(),

                    ui.hr(),

                    ui.p(
                        "The quantity variable ",
                        ui.span(quantity_var, class_="fw-bold"),
                        " does not possess a ",
                        ui.span("Numeric (Data-type)", class_="fw-bold"),
                        ui.br(),
                        "Please verify the selected quantity variable for any discrepancies."
                    ),

                    class_="alert alert-danger"
                )
            )
        
        else:

            return ui.TagList(
                    ui.div(
                        warning_header(),

                        ui.hr(),

                        ui.p(
                            "There are ",
                            ui.span("Order quantities with zero units or less", class_="fw-bold"),
                            " To filter out any quantities that are less than zero, ",
                            ui.span("please click on the ", class_="fw-bold"),
                            ui.span("Check input button", class_="fs-5 fw-bold"),
                            " below."
                        ),

                        class_="alert alert-warning"
                    ),

                    filter_out_zero_quantity_checkbox()
                )
        
    else:

        return ui.TagList(
        
            ui.div(
                success_header("Quantity"),

                ui.hr(),

                ui.p(
                    """ 
                    The Quantity variable selection has been 
                    """,
                    ui.span("Successful.", class_="fw-bold")
                ),

                class_="alert alert-success"
            ),

            filter_out_zero_quantity_checkbox(),
        )


def quantity_variable_selection_output(data: DataFrame, var_dict: dict):

    if var_dict["var_quantity"] not in ["no_selection", "no_variable"]:

        quntity_dict = check_quantity(data, var_dict)

        return quantity_select_output(
            quntity_dict, 
            quantity_var=var_dict["var_quantity"]
        )




# Revenue ---------------------------------------
def revenue_select_output(check_dict: dict, revenue_var: str):

    if check_dict["error"]:

        return ui.TagList(
            ui.div(
                error_header(),

                ui.hr(),

                ui.p(
                    "The revenue variable ",
                    ui.span(revenue_var, class_="fw-bold"),
                    " does not possess a ",
                    ui.span("Numeric (Data-type)", class_="fw-bold"),
                    "Please verify the selected revenue variable for any error"
                ),

                class_="alert alert-danger"
            )
        )
    
    else:

        return ui.TagList(
            ui.div(
                success_header("Revenue"),

                ui.hr(),

                ui.p(
                    """ 
                    The Revenue variable selection has been 
                    """,
                    ui.span("Successful.", class_="fw-bold")
                ),

                class_="alert alert-success"
            )
        )


def revenue_variable_selection_output(data: DataFrame, var_dict: dict):

    if var_dict["var_revenue"] not in ["no_selection", "no_variable"]:

        revenue_dict = check_revenue(data, var_dict)

        return revenue_select_output(revenue_dict, var_dict["var_revenue"])
    

    