from shiny import ui
from faicons import icon_svg
from shinywidgets import output_widget
import shiny.experimental as x



def numeric_summary_modal():

    return ui.modal_show(
        ui.modal(
            ui.TagList(
                ui.div(
                    ui.input_radio_buttons(
                        id="num_summary_choice",
                        label="Summarise Using:",
                        choices={
                            "table": "Table", 
                            "hist": "Histogram", 
                            "box": "Box Plot"
                        },
                        selected="table",
                        inline=True
                    ),
                ),

                ui.br(),

                x.ui.layout_sidebar(
                    x.ui.sidebar(
                        ui.output_ui(id="num_summary_additions"), 

                        id="num_summary_additions_sidebar", 
                        open="always",
                        width="200",
                        bg="#F5F5F5"
                    ),

                    ui.output_ui("numeric_summary_choice_output"),
                ),
                
            ),

            size="xl",
            easy_close=True
        )
    )


def trend_chart_modal():

    return ui.modal_show(
        ui.modal(
            ui.TagList(
                ui.row(
                    ui.column(
                        4,

                        ui.input_select(
                            id="trend_chart_variable",
                            label="Variable",
                            choices={
                                "var_revenue": "Revenue", 
                                "var_quantity": "Quantity"
                            },
                            selected="var_revenue"
                        ),
                    ),

                    ui.column(
                        4,

                        ui.input_select(
                            id="trend_chart_agg_func",
                            label="Aggregation",
                            choices={
                                "sum": "Total", 
                                "mean": "Average"
                            },
                            selected="sum"
                        ),
                    ),
                ),

                ui.br(),

                output_widget(id="trend_chart_output")
            ),

            size="xl",
            easy_close=True
        )
    )



def show_numeric_summary_ui(width: str = None):

    return ui.TagList(
        ui.input_action_button(
            id="show_numeric_summary",
            label="Show Numeric Summary",
            width=width,
            class_="btn-outline-dark",
            icon=icon_svg("arrow-up-right-from-square")
        ),
    )


def show_trend_summary_ui():

    return ui.input_action_button(
            id="show_trend_chart",
            label="Show Trend Chart",
            width="45%",
            class_="btn-outline-dark",
            icon=icon_svg("arrow-up-right-from-square")
        )



def run_analysis_btn(btn_id):

    return ui.input_action_button(
            id=btn_id,
            label="Run Analysis",
            icon=icon_svg("bolt"),
            class_="btn-outline-success mb-1"
        )


def download_input(download_id: str):

    return ui.TagList(
        ui.download_button(
            id=download_id, 
            label="Download",
            icon=icon_svg("download"),
            class_="btn-outline-dark"
        )
    )


# ABC -------------------------------------------
def abc_analysis_ui(): 

    return ui.TagList(
                ui.br(), 

                ui.div(
                    ui.div(
                        ui.h5("ABC ANALYSIS", class_="fw-bold text-decoration-underline"), 

                        class_="analysis-title-container"
                    ),
                    
                    ui.br(),
                    
                    ui.row(
                        ui.column(
                            12,

                            show_numeric_summary_ui(),
                        ),

                        align="center"       
                    ),
                    
                    ui.br(), ui.hr(), ui.br(),

                    ui.row(
                        ui.column(
                            2,

                            ui.input_numeric(
                                id="a_percentege", 
                                label="Percentage of (A) Class",
                                value=80,
                                min=50, max=95, 
                                step=5
                            ),

                            ui.input_numeric(
                                id="b_percentege", 
                                label="Percentage of (B) Class",
                                value=15,
                                min=5, max=50, 
                                step=5
                            ),

                            ui.input_numeric(
                                id="c_percentege", 
                                label="Percentage of (C) Class",
                                value=5,
                                min=1, max=20, 
                                step=1
                            ), 

                            ui.br(),

                            run_analysis_btn("run_abc_analysis"),
                        ),

                        ui.column(
                            10,

                            ui.div(
                                ui.output_data_frame(id="abc_raw_table"),

                                class_="overflow-table"
                            )
                        )
                    ),

                    ui.br(),

                    ui.row(
                        ui.column(
                            12,

                            
                            ui.output_ui(id="show_abc_download")
                        ),

                        align="center"
                    ),
                    
                    class_="section-border p-3"
                )
            )


def abc_plot_ui(switch_label: str, switch_input_id: str, widget_ui_id: str, switch_value: bool = False):

    return ui.TagList(
        ui.row(
                ui.column(
                    3,
                    
                    ui.br(),

                    ui.input_switch(
                        id=switch_input_id,
                        label=switch_label,
                        value=switch_value
                    )
                ),

                ui.column(
                    9,

                     ui.div(
                        ui.output_ui(id=widget_ui_id)
                     )
                )
            )
    )



def abc_summary_ui():

    return ui.TagList(
        ui.div(
            ui.row(
                ui.column(
                    3,
                     ui.input_action_button(
                            id="show_abc_table_summary",
                            label="Show Table Summary",
                            class_="btn-outline-dark",
                            icon=icon_svg("table")
                     ),
                ),

                ui.column(
                    9,

                    ui.div(
                        ui.output_data_frame(id="abc_table_summary_output")
                    ),
                )
            ), 

            ui.br(), ui.hr(), ui.br(),

            abc_plot_ui(
                "Total Product", 
                "show_abc_product_plot", 
                "abc_product_ui",
                True
            ),

            ui.br(),

            abc_plot_ui("Total Demand", "show_abc_demand_plot", "abc_demand_ui"),

            ui.br(),

            abc_plot_ui("Total Revenue", "show_abc_revenue_plot", "abc_revenue_ui"),

            class_="section-border p-3"
        )
    )





# XYZ --------------------------------------------
def xyz_analysis_ui():
    return ui.TagList(
                ui.br(),

                ui.div(
                    ui.div(
                        ui.h5("XYZ ANALYSIS"), 

                        class_="analysis-title-container"
                    ),
                    
                    ui.br(),
                    
                    ui.row(
                        ui.column(
                            6,

                            show_numeric_summary_ui(width="45%"),

                            class_="mb-1"
                        ),

                        ui.column(
                            6,

                            show_trend_summary_ui(),

                            class_="mb-1" 
                        ),

                        align="center"       
                    ),
                    
                    ui.br(), ui.hr(), ui.br(),

                    ui.row(
                        ui.column(
                            2,

                            ui.input_numeric(
                                id="x_limit", 
                                label="Max Limit of (X) Class",
                                value=0.5,
                                min=0.01, max=1.0, 
                                step=0.1
                            ),

                            ui.input_numeric(
                                id="y_limit", 
                                label="Max Linit of (Y) Class",
                                value=1.0,
                                min=0.5, max=2.0, 
                                step=0.1
                            ),

                            ui.br(),

                            run_analysis_btn("run_xyz_analysis"),
                        ),

                        ui.column(
                            10,

                            ui.div(
                                ui.output_data_frame(id="xyz_raw_table"),

                                class_="analysis-center-table-container overflow-table"
                            ),
                        )
                    ),

                    ui.br(),

                    ui.row(
                        ui.column(
                            12,

                            ui.output_ui(id="show_xyz_download")
                        ),

                        align="center"
                    ),
                    
                    class_="section-border p-3"
                )
            )



def xyz_summary_ui():

    return ui.TagList(
        ui.div(
            ui.row(
                ui.column(
                    3,

                    ui.input_switch(
                        id="show_cv_summary",
                        label="Show CV. Summary",
                        value=False
                    )
                ),

                ui.column(
                    9,

                    ui.output_ui(id="show_cv_summary_ui")
                )
            ),

            ui.br(), ui.hr(), ui.br(),

            ui.row(
                ui.column(
                    3,

                    ui.input_switch(
                        id="show_xyz_summary_table",
                        label="Show Summary table",
                        value=True
                    )
                ),

                ui.column(
                    9,

                    ui.div(
                        ui.output_data_frame(id="xyz_summary_table_output"),

                        class_="abc-table-container overflow-table"
                    )
                )
            ),

            ui.br(), ui.hr(),

            ui.row(
                ui.column(
                    2,

                    ui.br(),

                    ui.input_switch(
                        id="show_xyz_summary_plot",
                        label="Show Summary Plot",
                        value=True
                    )
                ),

                ui.column(
                    9,

                    output_widget(id="xyz_summary_plot_output")
                )
            ),

            class_="section-border p-3"
        )
    )




# ABC-XYz -----------------------------------------
def abc_xyz_analysis_ui():

    return ui.TagList(
                ui.br(),

                ui.div(
                    ui.div(
                        ui.h5("ABC-XYZ ANALYSIS"), 

                        class_="analysis-title-container"
                    ),
                    
                    ui.br(),
                    
                    ui.row(
                        ui.column(
                            6,

                            show_numeric_summary_ui(width="45%"),

                            class_="mb-1"
                        ),

                        ui.column(
                            6,

                            show_trend_summary_ui(),

                            class_="mb-1"
                        ),

                        align="center"       
                    ),
                    
                    ui.br(), ui.hr(), ui.br(),

                    ui.row(
                        ui.column(
                            2,

                            ui.input_numeric(
                                id="ax_a_percentege", 
                                label="Percentage of (A) Class",
                                value=80,
                                min=50, max=95, 
                                step=5
                            ),

                            ui.input_numeric(
                                id="ax_b_percentege", 
                                label="Percentage of (B) Class",
                                value=15,
                                min=5, max=50, 
                                step=5
                            ),

                            ui.input_numeric(
                                id="ax_c_percentege", 
                                label="Percentage of (C) Class",
                                value=5,
                                min=1, max=20, 
                                step=1
                            ), 

                            ui.hr(),

                            ui.input_numeric(
                                id="ax_x_limit", 
                                label="Max Limit of (X) Class",
                                value=0.5,
                                min=0.01, max=1.0, 
                                step=0.1
                            ),

                            ui.input_numeric(
                                id="ax_y_limit", 
                                label="Max Linit of (Y) Class",
                                value=1.0,
                                min=0.5, max=2.0, 
                                step=0.1
                            ),

                            ui.hr(),
                            

                            ui.br(),

                            run_analysis_btn("run_ax_analysis")
                        ),

                        ui.column(
                            10,

                            ui.div(
                                ui.output_data_frame(id="ax_raw_table"),

                                class_="overflow-table"
                            )
                        )
                    ),

                    ui.br(),

                    ui.row(
                        ui.column(
                            12,

                            ui.output_ui(id="show_ax_download")
                        ),

                        align="center"
                    ),
                    
                    class_="section-border p-3"
                )
            )


def abc_xyz_plot_summary_ui(switch_label: str, switch_input: str, outplut_id: str):

    return ui.TagList(
        ui.row(
            ui.column(
                3,

                ui.br(),
                
                ui.input_switch(
                    id=switch_input,
                    label=switch_label,
                    value=False
                )
            ),

            ui.column(
                9,

                ui.output_ui(id=outplut_id)
            )
        )
    )



def abc_xyz_summary_ui():
    return ui.TagList(
        ui.div(
            ui.row(
                ui.column(
                    3,

                    ui.input_switch(
                        id="show_abc_xyz_summary_table",
                        label="Show Summary Table",
                        value=True
                    )
                ),

                ui.column(
                    9,

                    ui.div(
                        ui.output_data_frame(id="abc_xyz_table_summary_output"),

                        class_="abc-table-container overflow-table"
                    )
                )
            ),

            ui.br(), ui.hr(), ui.br(),

            abc_xyz_plot_summary_ui("Show Product Summary", "show_product", "ax_product_output"),

            ui.br(),

            abc_xyz_plot_summary_ui("Show Demand Summary", "show_demand", "ax_demand_output"),

            ui.br(),

            abc_xyz_plot_summary_ui("Show Revenue Summary", "show_revenue", "ax_revenue_output"),

            class_="section-border p-3"
        )
    )

