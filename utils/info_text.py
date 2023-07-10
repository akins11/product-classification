variable_info = {
    "var_sku": """
                A Stock Keeping Unit(SKU) is a number that is assigned to products to keep track of 
                stock levels.
                Ths (SKU Variable) is expected to encompass all the distinct product units. It
                is important to note that the SKU should represent a specific type of product,
                and not a collection of products that have been grouped together.
               """,
    "var_date": """ 
                You are required to input a (Date Variable) that corresponds to the time frame
                when each transaction occured. This variable should encompass all transaction 
                date for either a single year or multiple years. However, if the data include
                multiple years, only one year will be utilized for the analysis period.
                """,
    "var_quantity": """ 
                    The (Quantity Variable) should indicate the overall number of units of a product
                    that were sold during a specific time frame. It is worth noting that any occurances
                    where the quantity is zero or less can be removed from the data through filtering.
                    """,
    "var_revenue": """ 
                    The (Revenue Variable) should reflect the total sales revenue generated
                    from each product SKU present in the data. if any non-numeric characters such 
                    as "$" "," are included in the revenue variable, they will be removed.
                   """
}