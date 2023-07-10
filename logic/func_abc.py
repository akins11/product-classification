from pandas import DataFrame
from plotly.express import bar
from plotly.graph_objects import FigureWidget

import plotly.io as pio
pio.templates.default = "plotly_white"




def valid_scale(scale: list) -> dict:
    """
    Check the all percentage scale supplied add up to 100%

    :params
        scale: a list of all percentages for class A, B & C.

    :return
        a dictionary 
    """
    
    if sum(scale) != 100:
        return {"error": True, "message": "values supplied to `scale` dose not sum up to 100"}
    else:
        return {"error": False, "message": None}
    


def abc_analysis(data: DataFrame, var_dict: dict, scale: list = [80, 15, 5]) -> dict:

    """ 
    Assign (ABC) classification for each product(SKU).

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
        scale: A list of all percentages for class A, B & C.

    :return
        A dictionary of the classified sku data, error and message.
    """

    var_sku = var_dict["var_sku"]

    var_quantity = var_dict["var_quantity"]

    var_revenue = var_dict["var_revenue"]

    if sum(scale) != 100:

        raise ValueError("values supplied to `scale` dose not sum up to 100")

    def classify_abc_item(cum_percent):
    
        if cum_percent <= scale[0]:
            return 'A'
        elif cum_percent > scale[0] and cum_percent <= scale[0] + scale[1]:
            return 'B'
        else:
            return 'C'
    
    try:

        abc_df = (
                data
                    .groupby(var_sku)
                    .agg(
                        unique_purchases = (var_sku, "nunique"),
                        total_demand     = (var_quantity, "sum"), 
                        total_revenue    = (var_revenue, "sum")
                    )
                    .sort_values(by="total_revenue", ascending=False)
                    .reset_index()
                    .assign(
                        revenue_cumsum = lambda _: _["total_revenue"].cumsum(),
                        revenue_running_percent = lambda _: (_["revenue_cumsum"] / _["total_revenue"].sum()) * 100,
                        abc_class = lambda _: _["revenue_running_percent"].apply(classify_abc_item),
                        rank  = lambda _: _["revenue_running_percent"].rank().astype(int)
                    )
            )
    
        return {"data": abc_df, "error": False, "message": None}
    
    except:

        return {"data": None, "error": True, "message": "Problem with cumulative summary."}
    




def summarise_abc(data: DataFrame, var_dict: dict, clean_name: bool = False) -> DataFrame:

    """ 
    Summarise the ABC classification by returning the number of unique products,
    the total demand and revenue for each group.

    :params
        data: A dataframe containing the abc classes and also [`total_demand`, `total_revenue`].
        var_dict: A dictionary of all the app variable names.
        clean_name: Whether to clean the column names.

    :return
        A summary dataframe.
    """

    f_tbl =  (
        data
            .groupby("abc_class")
            .agg(
                total_products = (var_dict["var_sku"], 'nunique'),
                total_demand   = ('total_demand', "sum"),
                total_revenue  = ('total_revenue', "sum")
            )
            .reset_index()
    )

    if clean_name:

        f_tbl.columns = f_tbl.columns.str.replace("_", " ").str.title()

        f_tbl = f_tbl.rename(columns={"Abc Class": "ABC Class"})

    return f_tbl




def abc_plot(data: DataFrame, plt_var: str):

    """ 
    A graphical summary of all products in each ABC class

    :params
        data: abc summary dataframe with `total products`, `total demand` and `total revenue`
        plt_var: One of the mentioned variable above.

    :return
        A plotly express object
    """

    data = data.assign(prop = lambda _: round((_[plt_var] / _[plt_var].sum())*100, 2))

    if plt_var == "total_products":

        y_label = "No. Products"
        title = "Number of Products in Each (ABC) Class"

    elif plt_var == "total_demand":

        y_label = "Qty. Demand"
        title = "Total Quantity Demand by (ABC) Class"

    else:

        y_label = "Revenue"
        title = "Total Revenue by (ABC) Clas"

    fig = FigureWidget(
        data=bar(
            data_frame=data,
            x="abc_class",
            y=plt_var,
            title=title,
            labels={"abc_class": "Class", plt_var: y_label},
            hover_data=["prop"],
            color_discrete_sequence=["#0E9594"],
            height=500
        )
    )

    fig.update_traces(
        hovertemplate=f"Class = <b>%{{x}}</b> <br> {y_label}  = %{{y:,}} <br> Percentage = %{{customdata[0]}}%",
        hoverlabel={"font_size": 18},
    )

    fig.update_layout(
        modebar=dict(
            remove=["zoomIn2d","zoomOut2d", "select2d", "pan2d", "autoScale2d",
                    "lasso2d", "zoom2d", "logo"]
        )
    )

    return fig 