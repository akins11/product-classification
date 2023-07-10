from pandas import DataFrame

from plotly.graph_objects import Figure, FigureWidget
from plotly.express import line, histogram

import plotly.io as pio
pio.templates.default = "plotly_white"



def trend_plot(data: DataFrame, var_dict: dict, plt_var: str, agg_fun: str):

    """ 
    Monthly trend value either revenue or quantity.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
        plt_var: The variable to summarise. Either 'var_quantity' or 'var_revenue'
        stats: The type of aggregate summary to use. Either 'sum' or 'mean'

    :return
        A plotly express object.
    """

    unique_month = data["month"].unique().tolist()

    month_dict = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 
                  7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

    relabel = {k: v for k, v in month_dict.items() if k in unique_month}   
    
    var = var_dict[plt_var]

    f_tbl = (
        data
        .groupby("month")[var]
        .agg(agg_fun)
        .reset_index()
        .assign(month = lambda _: _["month"].map(relabel))
        .assign(month = lambda _: _["month"].astype("category").cat.reorder_categories(relabel.values(), ordered=True))
    )

    agg_label = "Average" if agg_fun == "mean" else "Total"

    if plt_var == "var_revenue":

        y_label = "Revenue"
        plt_title = f"{agg_label} Revenue by Transaction Month"

    else:

        y_label = "Quantity"
        plt_title = f"{agg_label} Quantity Demand by Transaction Month"

    fig = FigureWidget(
        data=line(
            data_frame=f_tbl,
            x="month",
            y=var,
            title=plt_title,
            labels={"month": "", var: y_label},
            color_discrete_sequence=["#006D77"],
            markers=True,
            height=400
        )
    )

    fig.update_traces(
        line_width=3, 
        marker=dict(
            size=12,
            color="#FFFFFF",
            line=dict(
                width=2,
                color="#006D77"
            )
        ),
        hovertemplate=f" Month = <b>%{{x}}</b> <br> {y_label} = <b>%{{y}}</b> ",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=18,
            font=dict(color="#2F3E46"),
            bordercolor="#006D77"
        )
    )

    fig.update_layout(
        modebar=dict(
            remove=["zoomIn2d","zoomOut2d", "select2d", "pan2d", "autoScale2d",
                    "lasso2d", "zoom2d", "logo"]
        )
    )

    return fig



def xyz_analysis(data: DataFrame, var_dict: dict, scale: list = [0.5, 1.0]) -> dict:

    """ 
    Assign (XYZ) categories to each SKU based on their coefficient of 
    variation (CV) in order quantity.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
        scale: a list of two CV that will be used in grouping products in XYZ classes.

    :return
        A dictionary with the XYZ class data frame, error, message.
    """

    var_sku = var_dict["var_sku"]

    var_quantity = var_dict["var_quantity"]

    def classify_xyz_item(cov): 
        
        if cov <= scale[0]:
            return 'X'
        elif cov > scale[0] and cov <= scale[1]:
            return 'Y'
        else:
            return 'Z'

    xyz_df = (
        data
            .groupby([var_sku, "month"])[var_quantity]
            .sum()
            .reset_index()
            .pivot(index=var_sku, columns="month", values=var_quantity)
            .fillna(0)
            .add_prefix("M")
            .reset_index()
            .rename(index={"month": "index"})
    )

    xyz_df.columns.name = ""

    try:

        xyz_df = xyz_df.assign(
            std_demand   = lambda d: d[[c for c in xyz_df.columns if "M" in c]].std(axis=1),
            total_demand = lambda d: d[[c for c in xyz_df.columns if "M" in c]].sum(axis=1),
            avg_demand   = lambda d: d["total_demand"] / 12,
            cov_demand   = lambda d: d["std_demand"] / d["avg_demand"],
            xyz_class    = lambda d: d["cov_demand"].apply(classify_xyz_item)
        )

        return {"data": xyz_df, "error": False, "message": None}

    except:
        
        return {"data": None, "error": True, "message": "Could not create `Coefficient of variation` for demand"}




def cv_summary_table(data: DataFrame) -> DataFrame:

    """ 
    Coefficient of Variation in Demand tabular summary.

    :params
        data: a pandas dataframe with the `cov_demand` variable.

    :return
        A summarised dataframe.
    """

    return (
        data["cov_demand"]
            .agg(["min", "mean", "max"])
            .reset_index()
            .rename(columns={"index": "Stats", "cov_demand": "Coefficient of Variation"})
    )



def cv_summary_plot(data: DataFrame):

    """ 
    Coefficient of Variation in Demand graphical summary.

    :params
        data: a pandas dataframe with the `cov_demand` variable.

    :return
        A plotly Widget.
    """

    fig = FigureWidget(
        data=histogram(
            data_frame=data,
            x="cov_demand",
            title="Coefficient of Variation in Demand",
            labels={"cov_demand": "Coefficient of Variation"},
            color_discrete_sequence=["#83C5BE"],
            height=400
        )
    )

    fig.update_traces(
        hovertemplate=f" (CV) = <b>%{{x}}</b> <br> Count = <b>%{{y}}</b> ",
        hoverlabel=dict(
            font_size=18,
            font=dict(color="#2F3E46"),
            bordercolor="#2F3E46"
        )
    )

    fig.update_layout(
        modebar=dict(
            remove=["zoomIn2d","zoomOut2d", "select2d", "pan2d", "autoScale2d",
                    "lasso2d", "zoom2d", "logo"]
        )
    )

    return fig




def xyz_summary(data: DataFrame, clean_names: bool = False) -> DataFrame:

    """ 
    XYZ Classification summary.

    :params
        data: A pandas dataframe with an `xyz_class` variable.

    :return
        a pandas dataframe with the total products and demand, the average standard deviation
        of demand, average demand and coefficient of variation.
    """

    f_tbl = (
        data
            .groupby("xyz_class")
            .agg(
                total_product  = ("SKU", "nunique"),
                total_demand   = ("total_demand", "sum"),
                std_of_demand  = ("std_demand", "mean"),
                average_demand = ("avg_demand", "mean"),
                average_cov    = ("cov_demand", "mean")
            )
            .reset_index()
    )

    if clean_names:
        f_tbl.columns = f_tbl.columns.str.replace("_", " ").str.title()

        f_tbl = f_tbl.rename(columns={"Xyz Class": "XYZ Class"}).round(2)

    return f_tbl




def xyz_plot(data: DataFrame):

    """ 
    Total demand summary by XYZ class in each month.
    
    :params
        data: a pandas data with '  ' variable.

    :return
        A plotly object.
    """

    month_cols = [c for c in data.columns if "M" in c]

    month_dict = {"M1": "Jan", "M2": "Feb", "M3": "Mar", "M4": "Apr", "M5": "May", "M6": 
                  "Jun", "M7": "Jul", "M8": "Aug", "M9": "Sep", "M10": "Oct", "M11": "Nov", "M12": "Dec"}
    
    # Make sure only the present month index is applied to the data
    relabel = {k: v for k, v in month_dict.items() if k in month_cols}

    f_tbl = (
        data
            .groupby("xyz_class")[month_cols]
            .sum()
            .unstack(level="xyz_class")
            .reset_index()
            .rename(columns={0: "total_demand", "": "month"})
            .assign(month = lambda _: _["month"].map(relabel))
            .assign(
                month = lambda _: _["month"].astype("category").cat.reorder_categories(relabel.values(), ordered=True),
                xyz_class = lambda _: _["xyz_class"]+ " " + "Class"
            )
    )

    
    fig = FigureWidget(
        data=line(
            data_frame=f_tbl,
            x="month",
            y="total_demand",
            facet_row="xyz_class",
            facet_row_spacing=0.05,
            title="(XYZ) Class by Total Quantity Order for each Month",
            labels={"total_demand": "", "month": ""},
            color_discrete_sequence=["#006D77"],
            markers=True,
            height=600
        )
    )

    fig.update_traces(
        line_width=2, 
        marker=dict(
            size=6,
            color="#FFFFFF",
            line=dict(
                width=2,
                color="#006D77"
            )
        ),
        hovertemplate=" <b>Quantity Order</b> <br> <b>%{y}</b> ",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=14,
            font=dict(color="#2F3E46"),
            bordercolor="#006D77"
        )
    )

    fig.update_yaxes(matches=None, tickformat=",")

    fig.for_each_annotation(
        lambda a: a.update(text=a.text.split("=")[-1])
    )

    fig.update_layout(
        modebar=dict(
            remove=["zoomIn2d","zoomOut2d", "select2d", "pan2d", "autoScale2d",
                    "lasso2d", "zoom2d", "logo"]
        )
    )

    return fig