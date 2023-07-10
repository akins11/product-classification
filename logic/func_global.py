from pandas import DataFrame, to_datetime
from collections import Counter


def check_data(data: DataFrame):
    
    """
    check that the supplied data is in the correct format. Such as a dataframe
    with a least 50 rows.

    params:
    data: a pandas dataframe
    """

    if isinstance(data, DataFrame):

        if data.shape[0] >= 50:

            return {"data": data, "error": False, "message": None}
        
        else:

            return {"data": None, "error": True, "message": "Upload data have less than 50 rows"}
        
    else:
        
        return {"data": None, "error": True, "message": "Data Upload is not in a Dataframe format"}
    


def extract_variables(data: DataFrame, var_names: list) -> DataFrame:
    """
    Select only the needed variables for the analysis,
    variables such as the `Date`, product `SKU`, `Quantity` sold, `Revenue`.
    Note: that the date should have at leat a full year of transaction data.

    params:
        data: the uploaded pandas data frame.
        var_names: a list of variable names to keep.

    return:
    a pandas dataframe.
    """

    try:
        return data[var_names]
    except:
        return None
    


def clean_date_variable(data: DataFrame, var_dict: dict) -> dict:
    """
    Clean the date variable

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.

    :return
        A dictionary with the data, an error if the convertion was not successful and a message.
    """
    
    date_var = var_dict["var_date"]

    if data[date_var].dtype != "<M8[ns]":

        try:
            data[date_var] = to_datetime(data[date_var])

            return {"data": data, "error": False, "message": None}
        
        except:
            # /!\ This error should halt the analysis. /!\
            return {
                "data": data, 
                "error": True, 
                "message": " Could not convert the selected date variable to a datetime data-type."
            }
        
    else:

        return {"data": data, "error": False, "message": None}
    


def detect_multiple_years(data: DataFrame, var_dict: dict) -> dict:
    """ 
    Detect if there are multiple years in the data.
    Note: The selected date variable must be a date data type.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.

    :return
        A dictionary of the number of years and boolean if multiple years is detected in the data.
    """

    date_var = var_dict["var_date"]

    try:
        number_years = data[date_var].dt.year.nunique()

        unique_year = data[date_var].dt.year.unique().tolist()

        if len(unique_year) == 1:

            for year in unique_year:
                unique_year = year

        if number_years > 1:
            return {"is_multiple": True, "n_unique": number_years, "unique": unique_year, "error": False}
        else:
            return {"is_multiple": False, "n_unique": number_years, "unique": unique_year, "error": False}
    except:
        return {"is_multiple": False, "n_unique": 0, "unique": 0, "error": True}



def date_summary(data: DataFrame, var_dict: dict, query: str = 'all') -> DataFrame:

    """ 
    Create a summary of the number of months in each year.
    NOTE: The date variable must be a date data type.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
        query: Filter only the needed number of months. must be either ['all', 'twelve', or 'six_above'].

    return:
        A Summary Dataframe.
    """

    date_var = var_dict["var_date"]

    wk_df = DataFrame()

    try:
        wk_df = (
            wk_df
                .assign(year  = data[date_var].dt.year,
                        month = data[date_var].dt.month)
                .groupby("year")["month"]
                .agg("nunique")
                .reset_index()
                .sort_values(by="month", ascending=False)
        )

        if query == 'all':

            summary_df = wk_df

        elif query == 'twelve':

            summary_df = wk_df.query("month == 12")

        else:

            summary_df = wk_df.query("month >= 6")

        summary_df.columns = ["Year", "No. of Months"]

        return {"data": summary_df, "error": False, "message": None}
    
    except:
        return {
            "data": None, 
            "error": True, 
            "message": "Problem encountered while trying to summarise the date variable."
        }
    


def recommended_year(data: DataFrame, var_dict: dict) -> int:
    """ 
    Filter the year with the highest number of months and also the most recent.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
    
    :require
        `date_summary()` function.

    :return
        A single year integer.
    """

    summary_dict = date_summary(data, var_dict, "all")

    if summary_dict["error"]:

        return {"error": True, "message": summary_dict["message"],  "value": None}
    
    else:
        
        year = summary_dict["data"].head(1)["Year"].values

        for yr in year: year = yr

        return {"error": False, "message": None, "value": year}



def check_sku(data: DataFrame, var_dict: dict) -> dict:
    """
    A check on the number of unique SKU in the data.
    NOTE: only data with multiple skus is valid.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.

    :return
        A dict with an error & message keys indicating whether there are multiple sku.
    """

    if data[var_dict["var_sku"]].nunique() == 1:

        return {"error": True, "message": "only one unique `sku` detected"}
    
    else:

        return {"error": False, "message": None}


def check_quantity(data: DataFrame, var_dict: dict) -> dict:
    
    """ 
    Check on Zero order quantity in the dataset
    NOTE: only SKUs with order qunatity greater than zero are expected.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.

    :return
        a dictionary with the defunct data, True error and message if there are quantities 
        less than or equal to zero, else False error.
    """

    qty_var = var_dict["var_quantity"]

    if data[qty_var].dtype in ["float64", "int64"]:

        data = data.query(f"{qty_var} <= 0")

    else:

        return {"data": None, "error": True, "message": "The variable supplied is not numeric"}

    if data.shape[0] > 1:

        return {"data": data, "error": True, "message": "Some of the `quantity` are zero or less than zero"}
    
    else:

        return {"data": None, "error": False, "message": None}



def check_revenue(data: DataFrame, var_dict: dict) -> dict:
    """
    A check on the revenue data type.
    NOTE: only a numeric data type of revenue is expected. 

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
    
    :return
        A dictionary with the following keys: error, message.
    """

    revenue_var = var_dict["var_revenue"]

    if data[revenue_var].dtype in ["float64", "int64"]:

        return {"error": False, "message": None}
    
    else:
        
        return {"error": True, "message": "Revenue variable is not a numeric data type."}



def organize_data(data: DataFrame, var_dict: dict, year: int, drop_zero_qty: bool = False) -> dict:

    """ 
    Filter analysis year, drop zero quantity.

    :params
        data: A pandas dataframe.
        var_dict: A dictionary of all the app variable names.
        year: The analysis year.
        drop_zero_qty: Whether to drop all records with zero or less than zero quantity.

    :return
        A dict with the cleaned data, error and message.
    """

    date_var = var_dict["var_date"]

    revenue_var = var_dict["var_revenue"]

    try:

        data = (
            data
            .assign(year  = data[date_var].dt.year,
                    month = data[date_var].dt.month)
            .query(f"year == {year}")
            .drop(columns="year")
        )
            
        if data[revenue_var].dtype not in ["float64", "int64"]:
            for punct in ["$", ","]:
                data[revenue_var] = data[revenue_var].str.replace(punct, "", regex=False)
                data[revenue_var] = data[revenue_var].astype("float64")

    except:

        return {"data": data, "error": True, "message": "Revenue falied to parse to numeric"}

    try:

        if data[revenue_var].dtype in ["float64", "int64"]:
            
            quntity_var = var_dict["var_quantity"]

            if drop_zero_qty:

                data[quntity_var] = data[quntity_var].astype("int64")

                data = data.query(f"{quntity_var} > 0")

            else:

                data[quntity_var] = data[quntity_var].astype("int64")

    except:

        return {"data": data, "error": True, "message": "Quantity variable encountered a parsing problem"}

    if data.shape[0] != 0:

        return {"data": data, "error": False, "message": None}
    
    else:
        
        return {"data": data, "error": True, "message": "Data cleaning returned zero rows"}



def check_selected_variables(var_dict: dict) -> dict:
    """
    Check if all variables have been selected.

    :params
         var_dict: A dictionary of all the app variable names.

    :return
        A dictionary with all none selected variables if available.
    """
    
    non_selected = [key for key, val in var_dict.items() if val in ["no_selection", "no_variable"]]

    # if len(non_selected) == 0:

    #     is_all_selected = True

    # else:

    #     is_all_selected = False

    is_all_selected = True if len(non_selected) == 0 else False

    ui_dict = {"var_sku": "SKU", "var_date": "Date", "var_quantity": "Quantity", "var_revenue": "Revenue"}

    non_selected_vars = [val for key, val in ui_dict.items() if key in non_selected]

    return {"is_all_selected": is_all_selected, "non_selected_vars": non_selected_vars}



def extract_duplicate_variable(var_dict: dict):
    """ 
    Extract all variable that have been selected more than once.

    :param
        var_dict: A dictionary of all the app variable names.

    :return
        A list of variables selected more than once.
    """

    seleted_vars = var_dict.values()

    counts = Counter(seleted_vars)

    return [key for key, value in counts.items() if value > 1]