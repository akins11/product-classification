from pandas import DataFrame

from plotly.graph_objects import Figure, FigureWidget
from plotly.express import bar

from logic.func_abc import abc_analysis
from logic.func_xyz import xyz_analysis




def abc_xyz_analysis(
        data: DataFrame, 
        var_dict: dict, 
        abc_scale: list = [80, 15, 5], 
        xyz_scale: list = [0.5, 1]
) -> dict:

    """ 
    Assign ABC and XYZ class to each product (SKU).

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
        abc_scale: a list of all percentages to be used for assigning the A, B & C class.
        xyz_scale: a list of two CoV which will be used to group products in XYZ classes.

    :return
        A dictionary with the classification data, error and message.
    """

    var_sku = var_dict["var_sku"]

    abc_cols = [var_sku, "total_revenue", "abc_class"]

    xyz_cols = [var_sku, "std_demand", "total_demand", "avg_demand", "cov_demand", "xyz_class"]

    try:
        abc = abc_analysis(data=data, var_dict=var_dict, scale=abc_scale)

        if abc["error"]:

            return {"data": None, "error": True, "message": f"ABC classification failed || {abc['message']}"}
        
        else:

            abc = abc["data"][abc_cols]


        xyz = xyz_analysis(data=data, var_dict=var_dict, scale=xyz_scale)

        if xyz["error"]:

            return {"data": None, "error": True, "message": f"XYZ classification failed || {xyz['message']}"}
        
        else:

            xyz = xyz["data"][xyz_cols]


        abc_xyz_df = (
            abc
                .merge(xyz, how="left", on=var_sku)
                .assign(abc_xyz_class = lambda _: _["abc_class"].astype(str) + _["xyz_class"].astype(str))
        )

        return {"data": abc_xyz_df, "error": False, "message": None}

    except:

        return {"data": None, "error": True, "message": "ABC-XYZ failed"}
    



def abc_xyz_summary_table(data: DataFrame, edit_data: bool = False) -> DataFrame:

    """ 
    ABC and XYZ class summary table.

    :params
        data: data: A pandas dataframe with the abc_xyz class.
        edit_data: If true, the columns and rows will be transformed for clearity.

    :return
        A summarised dataframe.
    """

    f_tbl = (
        data
            .groupby("abc_xyz_class")
            .agg(
                total_sku     = ("SKU", 'nunique'),
                total_demand  = ('total_demand', "sum"),
                avg_demand    = ('avg_demand', 'mean'),    
                total_revenue = ('total_revenue', "sum")
            )
            .reset_index()
    )

    if edit_data:
        f_tbl.columns =  f_tbl.columns.str.replace("_", " ").str.title()
        f_tbl = f_tbl.rename(columns={"Abc Xyz Class": "ABC-XYZ Class"})

        f_tbl = f_tbl.round(2)

    return f_tbl




def abc_xyz_plot(data: DataFrame, plt_var):

    """ 
    ABC and XYZ class plot summary.

    :params
        data: A pandas dataframe with the `abc_xyz class` and also the plt_var.
        plt_var: The variable to summarise by abc analysis.

    :return
        A plotly object. 
    """

    f_tbl = data.assign(prop = round((data[plt_var] / data[plt_var].sum())*100, 2))

    color_list = ["#0D5C63", "#0D5C63", "#0D5C63", "#44A1A0", "#44A1A0", "#44A1A0", "#037971", "#037971", "#037971"]

    if plt_var == "total_sku":

        y_label = "No. Products"
        plt_title = "Number of Products by (ABC-XYZ) Class"

    elif plt_var == "total_demand":

        y_label = "Demand"
        plt_title = "Total Quantity Demand by (ABC-XYZ) Class"

    else:

        y_label = "Revenue"
        plt_title = "Total Revenue by (ABC-XYZ) Class"

    
    fig = FigureWidget(
        data=bar(
            data_frame=f_tbl,
            x="abc_xyz_class",
            y=plt_var,
            color="abc_xyz_class",
            title=plt_title,
            labels={plt_var: y_label, "abc_xyz_class": ""},
            hover_data=["prop"],
            color_discrete_sequence=color_list,
            height=500
        )
    )


    fig.update_traces(
        showlegend=False,
        hovertemplate=f" Class = <b>%{{x}}</b> <br> {y_label} = <b>%{{y}}</b> <br> Percentage = <b>%{{customdata[0]}}%</b><extra></extra>",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=18,
            font=dict(color="#2F3E46"),
            bordercolor="#006D77"
        )
    )

    fig.update_yaxes(tickformat=",")

    fig.update_layout(
        modebar=dict(
            remove=["zoomIn2d","zoomOut2d", "select2d", "pan2d", "autoScale2d",
                    "lasso2d", "zoom2d", "logo"]
        )
    )

    return fig