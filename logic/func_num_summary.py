from pandas import DataFrame

from plotly.graph_objects import Figure, FigureWidget
from plotly.express import histogram, box

import plotly.io as pio
pio.templates.default = "plotly_white"


def numeric_summary_table(data: DataFrame, var_dict: dict) -> dict:

    """
    Tabular description summary of order quantity and revenue.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
    
    :return
        A dictionary containing descriptive summary.
    """

    quantity_var = var_dict["var_quantity"]

    revenue_var = var_dict["var_revenue"]

    try:

        desc_df = (
            data[[quantity_var, revenue_var]]
                .describe()
                .reset_index()
                .query("index != 'count'")
                .round(3)
                .rename(columns= {"index": "Stat", quantity_var: "Quantity"})
        )

        return {"data": desc_df, "error": False, "message": None}

    except:

        return {"data": None, "error": True, "message": "problem with numeric description table summary"}
    



def numeric_summary_plot(
        data: DataFrame, 
        var_dict: dict, 
        variable: str = "var_quantity", 
        output: str = "hist", 
        n_bins: int = 30,
        log: bool = False
):

    """ 
    Graphical description summary of order quantity and revenue.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
        variable: The variable to summarise. Either ['var_quantity', 'var_revenue']
        output: The type of graph to return. either ['hist' for histogram or 'box' for boxplot].
    
    :return
        A plotly object.
    """

    var = var_dict[variable]

    clean_title = str.replace(var, "_", " ").title()

    plot_title = f"Distribution of {clean_title}"

    fill_color = ["#83C5BE"]

    if output == "hist":

        fig = FigureWidget(
            data=histogram(
                data_frame=data,
                x=var,
                nbins=n_bins,
                opacity=0.8,
                log_y=log,
                labels={var: clean_title},
                title=plot_title,
                color_discrete_sequence=fill_color,
                height=400
            )
        )
        
    else:

        fig = FigureWidget(
            data=box(
                data_frame=data,
                y=var,
                labels={var: clean_title},
                title=plot_title,
                color_discrete_sequence=fill_color,
                height=400
            )
        )


    fig.update_layout(
        modebar=dict(
            remove=["zoomIn2d","zoomOut2d", "select2d", "pan2d", "autoScale2d",
                    "lasso2d", "zoom2d", "logo"]
        )
    )
    
    return fig