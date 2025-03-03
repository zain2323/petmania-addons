from . import models
from odoo import api, SUPERUSER_ID

def pre_init(cr):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    get_all_sales_data(cr)
    get_division_wise_abc_sales_analysis_data(cr)


def get_all_sales_data(cr):
    query = """
        -- DROP FUNCTION public.get_sales_data(integer[], integer[], integer[], integer[], date, date);

        CREATE OR REPLACE FUNCTION public.get_all_sales_data(
            IN company_ids integer[],
            IN product_ids integer[],
            IN category_ids integer[],
            IN warehouse_ids integer[],
            IN start_date date,
            IN end_date date)
          RETURNS TABLE(company_id integer, company_name character varying, product_id integer, product_name character varying, product_category_id integer, category_name character varying, warehouse_id integer, warehouse_name character varying, sales_qty numeric, sales_amount numeric) AS
        $BODY$
                BEGIN
                    Return Query
                    Select 	
                        cmp_id, cmp_name, p_id, prod_name, categ_id, cat_name, wh_id, ware_name, sum(T.sales_qty) as total_sales, sum(T.sales_amount) as total_sales_amount
                    From
                    (	

                SELECT 
                    foo.cmp_id,
                    foo.cmp_name,
                    foo.p_id,
                    foo.prod_name,
                    foo.categ_id,
                    foo.cat_name,
                    foo.wh_id,
                    foo.ware_name,
                    foo.sales_amount,
                    foo.sales_qty
                FROM 
                ( 
                    SELECT 
                        so.company_id as cmp_id,
                        cmp.name as cmp_name,
                        sol.product_id as p_id,
                        pro.default_code as prod_name,
                        pt.categ_id,
                        cat.complete_name as cat_name,
                        so.warehouse_id as wh_id,
                        ware.name as ware_name,
                        Round(sol.price_subtotal /
                        CASE COALESCE(so.currency_rate, 0::numeric)
                            WHEN 0 THEN 1.0
                            ELSE so.currency_rate
                        END, 2) AS sales_amount,
                        Round(sol.product_uom_qty / u.factor * u2.factor,2) AS sales_qty
                    FROM sale_order_line sol
                        JOIN sale_order so ON sol.order_id = so.id
                        Inner Join product_product pro ON sol.product_id = pro.id
                        Inner Join product_template pt ON pro.product_tmpl_id = pt.id
                        Inner Join uom_uom u ON u.id = sol.product_uom
                        Inner Join uom_uom u2 ON u2.id = pt.uom_id
                        Inner Join res_company cmp on cmp.id = so.company_id
                        Inner Join stock_warehouse ware on ware.id = so.warehouse_id 
                        Inner Join product_category cat on cat.id = pt.categ_id
                    WHERE so.state::text = ANY (ARRAY['sale'::character varying::text, 'done'::character varying::text])  
                    and so.date_order >= start_date and so.date_order <= end_date
                    --company dynamic condition
                    and 1 = case when array_length(company_ids,1) >= 1 then 
                        case when so.company_id = ANY(company_ids) then 1 else 0 end
                        else 1 end
                    --product dynamic condition
                    and 1 = case when array_length(product_ids,1) >= 1 then 
                        case when sol.product_id = ANY(product_ids) then 1 else 0 end
                        else 1 end
                    --category dynamic condition
                    and 1 = case when array_length(category_ids,1) >= 1 then 
                        case when pt.categ_id = ANY(category_ids) then 1 else 0 end
                        else 1 end
                    --warehouse dynamic condition
                    and 1 = case when array_length(warehouse_ids,1) >= 1 then 
                        case when so.warehouse_id = ANY(warehouse_ids) then 1 else 0 end
                        else 1 end
                        
                ) foo
                    )T
                    group by cmp_id, cmp_name, p_id, prod_name, categ_id, cat_name, wh_id, ware_name;

                END; 

                $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000;
    """
    cr.execute(query)

def get_division_wise_abc_sales_analysis_data(cr):
    query = """
        -- DROP FUNCTION public.get_abc_sales_analysis_data(integer[], integer[], integer[], integer[], date, date, text);
        
        CREATE OR REPLACE FUNCTION public.get_division_wise_abc_sales_analysis_data(
            IN company_ids integer[],
            IN product_ids integer[],
            IN category_ids integer[],
            IN warehouse_ids integer[],
            IN start_date date,
            IN end_date date,
            IN abc_analysis_type text)
          RETURNS TABLE
          (
            company_id integer, company_name character varying, product_id integer, product_name character varying, 
            product_category_id integer, category_name character varying, warehouse_id integer, warehouse_name character varying,
            sales_qty numeric, sales_amount numeric, sales_amount_per numeric, cum_sales_amount_per numeric, analysis_category text
        ) AS
        $BODY$
                BEGIN
                    Return Query
                    
                    with all_data as (
                        Select * from get_sales_data_v2(company_ids, product_ids, category_ids, warehouse_ids, start_date, end_date)
                    ),
                    warehouse_wise_abc_analysis as(
                        Select a.warehouse_id, a.warehouse_name, sum(a.sales_qty) as total_sales, sum(a.sales_amount) as total_sales_amount
                        from all_data a
                        group by a.warehouse_id, a.warehouse_name
                    )
        
                    Select final_data.* from 
                    (
                        Select 
                            result.*,
                            case 
                                when result.cum_sales_amount_per < 80 then 'A' 
                                when result.cum_sales_amount_per >= 80 and result.cum_sales_amount_per <= 95 then 'B'
                                when result.cum_sales_amount_per > 95 then 'C'
                            end as analysis_category 
                        from
                        (
                            Select 
                                *, 
                                sum(cum_data.sales_amount_per) 
                    over (partition by cum_data.warehouse_id order by cum_data.warehouse_id, cum_data.sales_amount_per desc rows between unbounded preceding and current row) as cum_sales_amount_per
                            from 
                            (
                                Select 
                                    all_data.*, 
                                    case when wwabc.total_sales_amount <= 0.00 then 0 else 
                                        Round((all_data.sales_amount / wwabc.total_sales_amount * 100.0)::numeric,2) 
                                    end as sales_amount_per
                                from all_data
                                    Inner Join warehouse_wise_abc_analysis wwabc on all_data.warehouse_id = wwabc.warehouse_id 
                                order by sales_amount_per desc
                            )cum_data
                        )result
                    )final_data
                    where 
                    1 = case when abc_analysis_type = 'all' then 1 
                    else
                        case when abc_analysis_type = 'high_sales' then 
                            case when final_data.analysis_category = 'A' then 1 else 0 end
                        else 
                            case when abc_analysis_type = 'medium_sales' then 
                                case when final_data.analysis_category = 'B' then 1 else 0 end
                            else 
                                case when abc_analysis_type = 'low_sales' then 
                                    case when final_data.analysis_category = 'C' then 1 else 0 end
                                else 0 end
                
                            end
                        end
                    end;
                    
                END; $BODY$
          LANGUAGE plpgsql VOLATILE
          COST 100
          ROWS 1000;
    """
    cr.execute(query)